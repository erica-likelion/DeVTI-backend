import random
import math

from .category_score import get_category_score
from .wagging_score import get_wagging_score
from .parameter import TEAM_COUNT, PART_MIN


def _get_team_template(participant_list: list[dict]) -> list[str, int]:
    """
    참가자 수와 파트당 인원에 적절한 팀 매칭 템플릿을 생성

    input:
        - participant_list = [
            {
                "id": 1,
                "part": "pm",
                "team_vibe": "learning",
                "active_hours": "day",
                "meeting_preference": "offline",
                "openness": 0.73,
                "conscientiousness": 0.82,
                "extraversion": 0.41,
                "agreeableness": 0.78,
                "neuroticism": 0.32
            },
            {participant},
            {participant}
        ]

    return:
        - team_template = [
            {
                "pm": 1,
                "de": 1,
                "fe": 2,
                "be": 3
            }
            {team size},
            {team size},
        ]
    """
    part_total = {
        role: 0 for role in PART_MIN.keys()
    }  # 팀 매칭 참여자들의 파트별 인원수 통계값
    for participant in participant_list:
        if participant.get("part") not in part_total:
            print(
                f"id: {participant['id']} 참가자의 파트를 구분할 수 없습니다. (해당 인원을 제외하고 팀 매팅 진행)"
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
        return []

    team_template = [
        {part: part_total[part] // TEAM_COUNT for part in part_total.keys()}
        for _ in range(TEAM_COUNT)
    ]

    # 파트별로 남은 인원 분배
    leftovers = {part: part_total[part] % TEAM_COUNT for part in part_total.keys()}
    team_idx = 0

    for part, left_count in leftovers.items():
        for _ in range(left_count):
            team_template[team_idx][part] += 1
            team_idx = (team_idx + 1) % TEAM_COUNT

    return team_template


def random_team_assignment(participant_list: list[dict]) -> list[dict]:
    """
    초기 팀 매칭 템플릿을 랜덤으로 생성

    input:
        - participant_list = [
            {
                "id": 1,
                "part": "pm",
                "team_vibe": "learning",
                "active_hours": "day",
                "meeting_preference": "offline",
                "openness": 0.73,
                "conscientiousness": 0.82,
                "extraversion": 0.41,
                "agreeableness": 0.78,
                "neuroticism": 0.32
            },
            {participant},
            {participant}
        ]

        - team_template = [
            {
                "pm": 1,
                "de": 1,
                "fe": 2,
                "be": 3
            }
            {team size},
            {team size},
        ]

    return:
        - team_list = [
            [
                {
                    "id" 1,
                    "team_vibe": "빡세게",
                    "active_hours": "밤",
                    "meeting_preference": "온라인",
                    "waggee_list": [1, 3, 4, 5, 6, 9],
                    "openness": 0.84,
                    "conscientiousness": 0.34,
                    "extraversion": 0.56,
                    "agreeableness": 0.34,
                    "neuroticism': 0.99,
                },
                {},
                {},
                ...
            ],
            [],
            []
        ]
    """
    team_template = _get_team_template(participant_list)
    if not team_template:
        raise ValueError("요청하신 개수만큼의 팀을 생성할 수 없습니다.")

    part_groups = {part: [] for part in PART_MIN.keys()}

    # 참여자들을 파트별로 분리해서 저장
    for participant in participant_list:
        part = participant.get("part")
        part_groups[part].append(participant)

    # 파트별로 랜덤하게 셔플
    for part in part_groups.keys():
        random.shuffle(part_groups[part])

    team_list = []
    for team_id in range(len(team_template)):

        # 파트별로 인원 수 채우기
        team = []
        # team = {"id": team_id + 1}
        for part, required_count in team_template[team_id].items():

            if len(part_groups[part]) < required_count:
                raise ValueError(
                    f"팀 매칭에 필요한 파트원 수가 부족하여 매칭에 실패했습니다.\n파트: {part}\n필요 인원수: {required_count}\n남은 인원수: {len(part_groups[part])}"
                )

            for _ in range(required_count):
                person = part_groups[part].pop()
                team.append(person)

        team_list.append(team)

    return team_list


def evaluate_solution(team_list: list[list[dict]], waggings: list[dict] = None):
    """
    팀 매칭의 품질을 평가하는 함수
    낮은 점수일수록 좋은 매칭을 의미함 (최소화 문제)

    input:
        - team_list = [
            [
                {
                    "id" 1,
                    "team_vibe": "빡세게",
                    "active_hours": "밤",
                    "meeting_preference": "온라인",
                    "waggee_list": [1, 3, 4, 5, 6, 9],
                    "openness": 0.84,
                    "conscientiousness": 0.34,
                    "extraversion": 0.56,
                    "agreeableness": 0.34,
                    "neuroticism': 0.99,
                },
                {},
                {},
                ...
            ],
            [],
            []
        ]

        - waggings = [
            {
                "id": 1,
                "wagger": 1,
                "waggee": 3
            },
            {wagging info},
            {wagging info}
        ]

    return:
        - score: 알고리즘에 사용되는 점수
    """

    # 카테고리 점수 계산 (높을수록 좋음)
    category_scores = get_category_score(team_list)

    # 카테고리 점수의 평균과 분산 계산
    # 평균: 전체적인 매칭 품질
    # 분산: 팀 간 균형 (분산이 낮을수록 모든 팀이 고르게 좋음)
    category_mean = sum(category_scores) / len(category_scores)
    category_variance = sum(
        (score - category_mean) ** 2 for score in category_scores
    ) / len(category_scores)

    # 꼬리흔들기 점수 계산 (높을수록 좋음)
    wagging_scores, _ = get_wagging_score(team_list, waggings)

    # 꼬리흔들기에 성공하지 못한 사람의 수를 계산 후 패널티 부여
    wagging_fail_count = wagging_scores.count(0)

    wagging_mean = sum(wagging_scores) / len(wagging_scores)
    wagging_variance = sum(
        (score - wagging_mean) ** 2 for score in wagging_scores
    ) / len(wagging_scores)

    # 3. 최종 점수 계산 (낮을수록 좋게 변환)
    # 가중치 설정
    w_category_mean = 2.0  # 카테고리 매칭의 평균 품질
    w_category_var = 0.1  # 팀 간 카테고리 균형
    w_wagging_mean = 2.0  # 꼬리흔들기 매칭의 평균 품질
    w_wagging_var = 0.1  # 팀 간 꼬리흔들기 균형
    w_wagging_penalty = 50.0  # 꼬리흔들기 매칭 실패 패널티

    # 높은 점수를 낮은 비용으로 변환 (음수 사용)
    # 분산은 그대로 사용 (낮을수록 좋음)
    score = (
        -w_category_mean * category_mean  # 카테고리 평균이 높을수록 비용 감소
        + w_category_var * category_variance  # 분산이 낮을수록 비용 감소
        + -w_wagging_mean * wagging_mean  # 꼬리흔들기 평균이 높을수록 비용 감소
        + w_wagging_var * wagging_variance  # 분산이 낮을수록 비용 감소
        + w_wagging_penalty * wagging_fail_count
    )

    return score


def neighbor_solution(teams):
    """
    현재 팀 매칭에서 두 명의 멤버를 교환하여 이웃 해를 생성

    input:
        - teams = [
            [member1, member2, member3, ...],  # team 1
            [member1, member2, ...],           # team 2
            ...
        ]

    return:
        - new_teams: 새로운 팀 매칭 (깊은 복사)
    """
    # 깊은 복사로 원본 teams 훼손 방지
    new_teams = [[member.copy() for member in team] for team in teams]

    # 팀이 2개 미만이거나 전체 인원이 2명 미만이면 swap 불가
    if len(new_teams) < 2:
        return new_teams

    total_members = sum(len(team) for team in new_teams)
    if total_members < 2:
        return new_teams

    # 두 명의 멤버를 무작위로 선택하여 교환
    max_iter = 200
    for _ in range(max_iter):
        # 랜덤하게 두 개의 다른 팀 선택
        team_a_idx, team_b_idx = random.sample(range(len(new_teams)), 2)

        # 각 팀이 비어있지 않은지 확인
        if len(new_teams[team_a_idx]) == 0 or len(new_teams[team_b_idx]) == 0:
            continue

        # 각 팀에서 랜덤하게 한 명씩 선택
        person_a_idx = random.randint(0, len(new_teams[team_a_idx]) - 1)
        person_b_idx = random.randint(0, len(new_teams[team_b_idx]) - 1)

        person_a = new_teams[team_a_idx][person_a_idx]
        person_b = new_teams[team_b_idx][person_b_idx]

        # 같은 파트끼리만 교환 (파트 제약 유지)
        if person_a.get("part") == person_b.get("part"):
            # 교환 수행
            new_teams[team_a_idx][person_a_idx] = person_b
            new_teams[team_b_idx][person_b_idx] = person_a
            break

    return new_teams


def simulated_annealing(
    initial_solution,
    waggings=None,
    initial_temp=1.0,
    min_temp=0.001,
    cooling_rate=0.995,
    max_iterations=10000,
):
    current_solution = initial_solution
    current_score = evaluate_solution(current_solution, waggings)

    best_solution = current_solution
    best_score = current_score

    T = initial_temp

    iteration = 0
    while T > min_temp and iteration < max_iterations:

        # 1) neighbor 생성
        new_solution = neighbor_solution(current_solution)
        new_score = evaluate_solution(new_solution, waggings)

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
