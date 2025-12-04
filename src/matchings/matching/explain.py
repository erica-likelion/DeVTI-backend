"""
TODO:
    - 팀별로 카테고리 데이터에서 가장 일치도가 높은 것을 바탕으로 설명
    - 다른 팀에 비해 우리팀의 성격 유형이 어떤지를 설명 (다른팀 보다 외향적이에요! 활기차게 팀플해봐요) 어떻게 팀플을 해나가면 좋을지는 LLM에게 맏기기
"""

import json
from parameter import CATEGORY, PART_MIN
from category_score import _get_team_category_rate
from wagging_score import _get_wagging_dict
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()


def _get_team_info_list(team_list, waggings):
    """
    팀 매칭 결과에 대한 설명글을 작성하기 위해 LLM에 전달할 팀별 통계 데이터를 반환

    Args:
        - team_list = [
            [
                {
                    "id": 1,
                    "part": "",
                    "team_vibe": "learning",
                    "active_hours": "day",
                    "meeting_preference": "offline",
                    "ei": 0.65,
                    "sn": 0.73,
                    "tf": 0.42,
                    "jp": 0.58,
                    "devti": "골든 리트리버"
                },
                {member2},
                ...
            ],
            [],
            [],
            ...
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

    Returns:
        - team_info_list = [
            {
                "pm": 1,
                "de": 1,
                "fe": 3,
                "be": 2,
                "team_vibe": ("professional", 0.8),
                "active_hours": ("day", 0.5),
                "meeting_preference": ("online": 0.6),
                "ei": 0.5,
                "sn": 0.7,
                "tf": 0.9,
                "jp": 0.4,
                "poppy_list": ["골든 리트리버", "시바견", "불독", "말티즈"],
                "wagging_pairs": [["시바견(be)", "불독(de)"], ["시바견(fe)": "말티즈(be)"]] # 시바견이 불독, 말티즈를 좋아함
            },
            {team},
            ...
        ]
    """
    team_info_list = []
    wagging_dict = _get_wagging_dict(waggings)

    for team in team_list:
        team_info = {part: 0 for part in PART_MIN}

        # 파트별 인원수
        for member in team:
            team_info[member["part"]] += 1

        # 팀별 가장 높은 카테고리 데이터와 비율
        team_category_rate = _get_team_category_rate(team)
        for key, rate_dict in team_category_rate.items():
            max_value, rate = max(rate_dict.items(), key=lambda x: x[1])
            team_info[key] = (max_value, rate)

        # 팀별 mbti 통계
        ei_mean = sum([member["ei"] for member in team]) / len(team)
        sn_mean = sum([member["sn"] for member in team]) / len(team)
        tf_mean = sum([member["tf"] for member in team]) / len(team)
        jp_mean = sum([member["jp"] for member in team]) / len(team)
        team_info["ei"] = ei_mean
        team_info["sn"] = sn_mean
        team_info["tf"] = tf_mean
        team_info["jp"] = jp_mean

        # 팀에 있는 강아지 목록 추가
        team_info["poppy_list"] = [member["devti"] for member in team]

        # 꼬리흔들기 짝궁 구하기
        wagging_pairs = []
        for i in range(len(team)):
            member1 = team[i]
            waggees = wagging_dict.get(member1["id"], set())

            for j in range(len(team)):
                if i == j:
                    continue
                member2 = team[j]
                if member2["id"] in waggees:
                    wagging_pairs.append(
                        [
                            f"{member1["devti"]}({member1["part"]})",
                            f"{member2["devti"]}({member2["part"]})",
                        ]
                    )
        team_info["wagging_pairs"] = wagging_pairs

        team_info_list.append(team_info)

    return team_info_list


def get_matching_explanations(team_list):
    """
    Args:
        - team_list = [
            [
                {
                    "id": 1,
                    "part": "",
                    "team_vibe": "learning",
                    "active_hours": "day",
                    "meeting_preference": "offline",
                    "ei": 0.65,
                    "sn": 0.73,
                    "tf": 0.42,
                    "jp": 0.58,
                    "devti": "골든 리트리버"
                },
                {member2},
                ...
            ],
            [],
            [],
            ...
        ]

    Returns:
        - reasons: 각 팀마다 팀 매칭 설명을 담아서 반환
    """
    with open("sample_data/wagging.json", "r", encoding="utf-8") as f:
        waggings = json.load(f)
    team_info_list = _get_team_info_list(team_list, waggings)
    response = call_llm("gpt", team_info_list)

    return response


class TeamVibe(BaseModel):
    vibe: str
    score: float


class ActiveHours(BaseModel):
    hours: str
    score: float


class MeetingPreference(BaseModel):
    preference: str
    score: float


class Team(BaseModel):
    team_vibe: TeamVibe
    active_hours: ActiveHours
    meeting_preference: MeetingPreference
    ei: float
    sn: float
    tf: float
    jp: float
    poppy_list: list[str]
    reason: str


class TeamList(BaseModel):
    teams: list[Team]


def call_llm(team_info_list):
    """
    Arge:
        - type = "gemini" || "gpt"
    """
    with open("prompt/explain.txt", "r", encoding="utf-8") as f:
        prompt = f.read()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.beta.chat.completions.parse(
        model="gpt-5.1",
        messages=[
            {
                "role": "system",
                "content": prompt,
            },
            {"role": "user", "content": f"{team_info_list}"},
        ],
        response_format=TeamList,
    )
    return response.choices[0].message.parsed.teams
