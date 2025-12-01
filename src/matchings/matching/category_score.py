from math import log

CATEGORY = {
    # element: [name1, name2]
    "team_vibe": ["learning", "professional"],
    "active_hours": ["day", "night"],
    "meeting_preference": ["online", "offline"],
}


def get_category_score(team_list: list[list[dict]]) -> list[dict]:
    """
    모든 팀의 카테고리 데이터 점수를 반환

    input:
        - team_list = [
            [
                {member1},
                {member2},
                ...
            ],
            [],
            [],
            ...
        ]

    return:
        - category_score = [0.45, 0.88]
    """
    category_weight = _get_category_weight(team_list)
    weight_list = []
    for value_dict in category_weight.values():
        weight_list.extend(value_dict.values())
    max_weight = max(weight_list)  # 가장 큰 weight

    category_score = []

    for team in team_list:
        team_similarity = _get_team_similarity(team)
        team_score = 0

        for key, values in team_similarity.items():
            most_frequent_value, rate = sorted(
                [(value, team_similarity[key][value]) for value in values],
                key=lambda x: -x[1],
            )[0]
            weight = category_weight[key][most_frequent_value]
            score = rate * weight
            team_score += score
        team_score = round(team_score / len(team_similarity) / max_weight, 2) * 100
        category_score.append(team_score)

    return category_score


def _get_team_similarity(member_list: list[dict]) -> dict[dict]:
    """
    한 팀의 카테고리 데이터 유사도를 반환

    input:
        - member_list = [
            {member1},
            {member2},
            ...
        ]

    return:
        - similarity = {
            "team_vibe": {"learning": 0.65, "professional": 0.35},
            "active_hours": {},
            "meeting_preference: {}
        }
    """
    team_size = len(member_list)

    # 카테고리 개수를 저장할 딕셔너리
    team_category_count = {
        key: {value: 0 for value in values} for key, values in CATEGORY.items()
    }

    # team _category_count 업데이트
    for member in member_list:
        for category_key in CATEGORY:
            team_category_count[category_key][member[category_key]] += 1

    # 각 카테고리의 유사도를 저장 (카테고리가 일치하는 사람의 비율)
    similarity = {}
    for key, values in team_category_count.items():
        similarity[key] = {}  # 추가 필요
        value_total = sum(team_category_count[key][value] for value in values)

        for value in values:
            similarity[key][value] = round(
                team_category_count[key][value] / value_total, 2
            )

    return similarity


def _get_category_weight(team_list: list[list[dict]]) -> dict[dict]:
    """
    카테고리 데이터의 가중치 정보를 담은 딕셔너리를 반환

    input:
        - team_list = [
            [
                {member1},
                {member2},
                ...
            ],
            [],
            [],
            ...
        ]

    return:
        - category_weight = {
            team_vibe: {learning: 0.82, professional: 0.18},
            active_hours: {},
        }
    """
    # 카테고리 통계
    category_count = {
        key: {value: 0 for value in values} for key, values in CATEGORY.items()
    }
    for team in team_list:
        for member in team:
            for key in CATEGORY:
                category_count[key][member[key]] += 1

    # 카테고리별 가중치 계산
    category_weight = {}
    participant_count = sum([len(team) for team in team_list])

    # ex) team_vibe, [learning, professional]
    for key, values in category_count.items():
        value_total = sum(category_count[key][value] for value in values)
        category_weight[key] = {}

        for value in values:
            # 모든 참가자가 같은 카테고리를 선택한 경우에는 가중치를 1 (만점처리)
            if category_count[key][value] == participant_count:
                category_weight[key][value] = 1
            else:
                category_weight[key][value] = round(
                    -log(category_count[key][value] / value_total), 2
                )

    return category_weight
