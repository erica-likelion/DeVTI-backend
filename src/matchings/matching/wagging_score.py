def _get_wagging_dict(waggings: list[dict]) -> dict[set]:
    """
    Wagging 테이블 데이터를 받아서 {꼬리 흔들기 주체: [꼬리를 흔든 대상 리스트]} 형식으로 변환

    input:
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
        - wagging_dict = {
            wagger_id1: {1, 3, 4, },
            wagger_id2: {2, 5, 7, }
        }
    """
    wagging_dict: dict[int, set] = {}  # {wagger_id: (꼬리를 흔든 사람 목록)}
    for wagging in waggings:
        wagger, waggee = wagging["wagger"], wagging["waggee"]
        if wagger not in wagging_dict:
            wagging_dict[wagger] = set([waggee])
        else:
            wagging_dict[wagger].add(waggee)
    return wagging_dict


def get_wagging_score(team_list, waggings) -> tuple[list]:
    """
    모든 팀의 꼬리흔들기 점수를 담은 리스트 반환

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

        - weight: 꼬리흔들기가 팀 매칭에 반영되었을 경우 부여할 가중치 점수 (1 이상)

    return:
        - wagging_score = [0.34, 0.12, 0.56, ...] 모든 참가자들의 wagging 점수
        - wagging_score_per_team = [] 팀별 wagging 점수
    """
    wagging_dict = _get_wagging_dict(waggings)
    wagging_score = []  # 모든 참가자들의 꼬리 흔들기 점수를 저장
    wagging_score_per_team = []  # 팀 별로 꼬리흔들기 매칭 성공률을 저장

    for team in team_list:

        # 팀 멤버마다 꼬리 흔들기가 적중된 횟수 저장
        wagging_count = {member["id"]: 0 for member in team}

        for id in wagging_count.keys():
            waggees = wagging_dict.get(id, set())

            for other_id in wagging_count.keys():
                if id == waggees:
                    continue
                if other_id in waggees:
                    wagging_count[id] += 1

        wagging_score.extend(wagging_count.values())
        team_size = len(team)
        pair_count = team_size * (team_size - 1) // 2
        wagging_score_per_team.append(
            round(sum(wagging_count.values()) / (pair_count * 2), 2) * 100
        )

    return wagging_score, wagging_score_per_team
