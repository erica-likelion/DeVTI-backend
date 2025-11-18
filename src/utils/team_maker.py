import random
import math


# 향후 변수로 입력받을 값 (현재는 상수)
TEAM_COUNT = 5  # 생성할 팀의 개수
PART_MIN = {"pm": 0, "de": 1, "fe": 2, "be": 2}  # 파트별 최소 인원수


def get_team_size(participant_list: list[dict]) -> dict[str, int] | dict:
    """ """
    part_total = {
        role: 0 for role in PART_MIN.keys()
    }  # 팀 매칭 참여자들의 파트별 인원수 통계값
    for participant in participant_list:
        if participant.get("part") not in part_total:
            print(
                f"id: {participant["id"]} 참가자의 파트를 구분할 수 없습니다. (해당 인원을 제외하고 팀 매팅 진행)"
            )
            continue
        part_total[participant["part"]] += 1

    # TEAM_COUNT 만큼의 팀을 생성할 수 있는지 여부 판단
    team_max = min(
        (part_total[part] // min_cnt) if min_cnt > 0 else float("inf")
        for part, min_cnt in PART_MIN.items()
    )
    if TEAM_COUNT > team_max:
        print("설정한 팀의 개수만큼 팀을 생성할 수 없습니다.")
        return {}

    team_size = [
        {part: part_total[part] // TEAM_COUNT for part in part_total.keys()}
        for _ in range(TEAM_COUNT)
    ]

    # 파트별로 남은 인원 분배
    leftovers = {part: part_total[part] % TEAM_COUNT for part in part_total.keys()}
    team_idx = 0

    for part, left_count in leftovers.items():
        for _ in range(left_count):
            team_size[team_idx][part] += 1
            team_idx = (team_idx + 1) % TEAM_COUNT

    return team_size


def random_team_assignment(
    participant_list: list[dict], team_size: list[dict]
) -> list[dict]:

    print("팀 배정표")
    print(team_size)

    # 팀 배정표가 제대로 입력되지 않았을 경우
    if len(team_size) == 0:
        return []

    part_groups = {part: [] for part in team_size[0].keys()}

    # 참여자들을 파트별로 분리해서 저장
    for participant in participant_list:
        part = participant.get("part")
        part_groups[part].append(participant)

    # 파트별로 랜덤하게 셔플
    for part in part_groups.keys():
        random.shuffle(part_groups[part])

    print("파트별 셔플 결과")
    for part, lst in part_groups.items():
        print(f"{part}: {len(lst)}")

    teams = []
    for team_id in range(len(team_size)):

        # 파트별로 인원 수 채우기
        team = {"id": team_id + 1}
        for part, required_count in team_size[team_id].items():
            team[part] = []

            if len(part_groups[part]) < required_count:
                raise ValueError(
                    f"팀 매칭에 필요한 파트원 수가 부족하여 매칭에 실패했습니다.\n파트: {part}\n필요 인원수: {required_count}\n남은 인원수: {len(part_groups[part])}"
                )

            for _ in range(required_count):
                person = part_groups[part].pop()
                person = person.copy()  # 참가자 원본 데이터 훼손 방지
                team[part].append(person)

        teams.append(team)

    return teams


def evaluate_solution(
    teams: list[dict],
    waggings,
    low_c_threshold=0.5,
    w_n=1.0,
    w_e=1.0,
    w_c=2.0,
    w_wagging=3.0,
):
    """
    최종적으로 반환해야 하는 값:
    - 팀 내에서 서로에게 꼬리를 흔든 쌍의 개수
    - (각 팀에서 꼬리를 흔든 사람이 얼마나 속해있는지)

    - 팀의 외향성 평균이 어떤지
    - 성실도의 평균이 어떤지
    - 각 팀의 성격 유형 통계를 정리한 뒤, LLM에게 설명을 맡김
    """

    wagging_dict: dict[int, set] = _get_wagging_dict(waggings)

    for team in teams:
        team_members = []

        n_list = []
        e_list = []
        c_list = []
        for part in PART_MIN.keys():
            team_members.extend(team[part])

        team_members_id = set([member["id"] for member in team_members])

        # wagging 몇 개 성공했는지 계산 ------------------------------------------------------------------------------------
        single_wagging_count = 0
        double_wagging_count = 0

        for member1_id in team_members_id:
            if member1_id not in wagging_dict:  # 꼬리를 아무에게도 흔들지 않은 사람
                continue

            member1_waggees_id = wagging_dict[member1_id]
            for member2_id in team_members_id:
                if member1_id == member2_id:
                    continue
                if member2_id not in member1_waggees_id:
                    continue

                if (
                    member2_id in wagging_dict
                    and member1_id in wagging_dict[member2_id]
                ):  # 양방향 wagging
                    double_wagging_count += 1
                else:  # 단방향 wagging
                    single_wagging_count += 1

        # 성격 유형 계산 ------------------------------------------------------------------------------------
        team_n_means = []  # 팀별 N 값 평균
        team_e_stds = []  # 팀별 E 값 표준편차
        team_c_counts = []  # 높은 C 값을 가진 사람이 몇 명인지

        for member in team_members:
            n_list.append(member["neuroticism"])
            e_list.append(member["extraversion"])
            c_list.append(member["conscientiousness"])

        team_n_means.append(sum(n_list) / len(n_list))
        e_mean = sum(e_list) / len(e_list)
        e_var = sum([(e - e_mean) ** 2 for e in e_list]) / len(e_list)
        team_e_stds.append(e_var**0.5)
        high_c_count = sum(1 if c_value > low_c_threshold else 0 for c_value in c_list)
        team_c_counts.append(high_c_count)

    n_mean = sum(team_n_means) / len(team_n_means)
    n_var = sum((n - n_mean) ** 2 for n in team_n_means) / len(team_n_means)

    e_mean = sum(team_e_stds) / len(team_e_stds)

    c_penalty = 1 if sum(team_c_counts) == 0 else 0

    wagging_score = -(single_wagging_count + 2 * double_wagging_count)

    # 각 팀의 N 평균의 분산 최소화
    # 각 팀의 E 표준편차의 평균 최소화
    # 각 팀에 성실도가 높은 사람이 적어도 한 명
    score = w_n * n_var + w_e * e_mean + c_penalty * w_c + w_wagging * wagging_score
    return score


def neighbor_solution(teams):
    # 깊은 복사로 원본 teams 훼손 방지
    new_teams = []
    for team in teams:
        copied_team = {"id": team["id"]}
        for part in PART_MIN.keys():
            copied_team[part] = [p.copy() for p in team[part]]
        new_teams.append(copied_team)

    # 랜덤 파트 선택
    part = random.choice(list(PART_MIN.keys()))

    # 선택한 파트의 전체 사람 목록과 그들의 팀 인덱스 수집
    people = []
    for team_idx, team in enumerate(new_teams):
        for person in team[part]:
            people.append((team_idx, person))

    # 만약 해당 파트 인원수가 2명 미만이면 swap 불가
    if len(people) < 2:
        return new_teams

    # 두 사람 무작위 선택
    max_iter = 200
    for _ in range(max_iter):
        (team_a, person_a), (team_b, person_b) = random.sample(people, 2)
        if team_a == team_b:
            continue

        team_a_list = new_teams[team_a][part]
        team_b_list = new_teams[team_b][part]

        team_a_list.remove(person_a)
        team_b_list.remove(person_b)

        team_a_list.append(person_b)
        team_b_list.append(person_a)
        break

    return new_teams


def simulated_annealing(
    initial_solution,
    initial_temp=1.0,
    min_temp=0.001,
    cooling_rate=0.995,
    max_iterations=10000,
):
    current_solution = initial_solution
    current_score = evaluate_solution(current_solution)

    best_solution = current_solution
    best_score = current_score

    T = initial_temp

    iteration = 0
    while T > min_temp and iteration < max_iterations:

        # 1) neighbor 생성
        new_solution = neighbor_solution(current_solution)
        new_score = evaluate_solution(new_solution)

        # 2) score 차이
        delta = new_score - current_score

        # 3) 더 좋으면 무조건 채택
        if delta < 0:
            accept = True
        else:
            # 4) 더 나쁜 해는 확률적으로 채택
            p = math.exp(-delta / T)
            accept = random.random() < p

        if accept:
            current_solution = new_solution
            current_score = new_score

        # 5) best 업데이트
        if current_score < best_score:
            best_solution = current_solution
            best_score = current_score

        # 온도 감소
        T *= cooling_rate
        iteration += 1

    return best_solution, best_score


def _get_wagging_dict(waggings):
    """
    Wagging 테이블 데이터를 받아서 {꼬리 흔들기 주체: [꼬리를 흔든 대상 리스트]} 형식으로 변환
    """
    wagging_dict: dict[int, set] = {}  # {wagger_id: (꼬리를 흔든 사람 목록)}
    for wagging in waggings:
        wagger, waggee = wagging["wagger"], wagging["waggee"]
        if wagger not in wagging_dict:
            wagging_dict[wagger] = set([waggee])
        else:
            wagging_dict[wagger].add(waggee)
    return wagging_dict
