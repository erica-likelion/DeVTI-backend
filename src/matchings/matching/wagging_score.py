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


def get_wagging_score(team_list, waggings) -> list:
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
        - wagging_score = [0.34, 0.12, 0.56]
    """
    wagging_dict = _get_wagging_dict(waggings)
    wagging_score = []

    for team in team_list:
        single_wagging_count = 0
        double_wagging_count = 0
        team_id_list = [member["id"] for member in team]

        for i in range(len(team_id_list)):
            for j in range(i + 1, len(team_id_list)):
                member1_id = team_id_list[i]
                member2_id = team_id_list[j]

                member1_waggees = wagging_dict.get(member1_id, set())
                member2_waggees = wagging_dict.get(member2_id, set())

                if member2_id in member1_waggees:
                    if member1_id in member2_waggees:  # 양방향 매칭 성공
                        double_wagging_count += 1
                    else:  # 단방향 매칭 성공
                        single_wagging_count += 1
                elif member1_id in member2_waggees:  # 단방향 매칭 성공
                    single_wagging_count += 1

        team_size = len(team)
        pair_count = team_size * (team_size - 1) // 2  # 팀 개수는 반드시 1 이상
        team_score = (
            round((single_wagging_count * 0.5 + double_wagging_count) / pair_count, 2)
            * 100
        )
        wagging_score.append(team_score)

    return wagging_score
