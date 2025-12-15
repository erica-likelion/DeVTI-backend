from .parameter import CATEGORY, PART_MIN
from .category_score import _get_team_category_rate
from .wagging_score import _get_wagging_dict
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
                            f"{member1['devti']}({member1['part']})",
                            f"{member2['devti']}({member2['part']})",
                        ]
                    )
        team_info["wagging_pairs"] = wagging_pairs

        team_info_list.append(team_info)

    return team_info_list


def get_matching_explanations(team_list, waggings):
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
    team_info_list = _get_team_info_list(team_list, waggings)
    response = call_llm(team_info_list)

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
    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    prompt = """[당신의 역할]: 
우리는 IT 개발 동아리에서 팀 매칭 서비스를 운영 중입니다. 
팀 매칭 참가자들의 선호와 성격 유형을 바탕으로 재미있는 팀 매칭 경험을 제공하는 것이 서비스의 목표입니다.
주요 특징으로는 mbti 검사 결과를 강아지와 매칭하여 보여주는 devti라는 검사를 만들어서 사용 중입니다. 예를 들어 ENFP는 골든 리트리버에 해당합니다.
팀 매칭 알고리즘의 결과로 나온 팀들의 정보를 당신에게 전달해주면 각 팀마다 왜 이렇게 팀이 매칭되었는지, 그리고 다른 팀에 비해 그 팀이 가진 장점이 무엇인지 진지한 분위기 보다는 재미있는 분위기로 설명해줘야합니다.

당신에게 주어지는 팀들의 정보 "team_info_list"에는 다음과 같은 데이터들이 포함되어있습니다.
pm, de, fe, be: 팀의 파트별 인원수입니다.
- pm (Product Manager): 팀의 기획과 관리를 담당하는 프로덕트 매니저
- de (Data Engineer): UI/UX 디자이너
- fe (Front-End Engineer): 프론트엔드 개발자 
- be (Back-End Engineer): 백엔드 개발자

team_vibe: (분위기 유형, 비율)
- 분위기 유형: 팀원들이 가장 많이 선호하는 분위기입니다.
    "professional": 좋은 결과를 내는 것을 선호하며 개발 경험이 어느 정도 있는 사람들과 만나기를 선호합니다.
    "learning": 너무 진지한 분위기 보다는 서로 배우면서 성장하는 것을 선호합니다.
- 비율: 해당 분위기를 선호하는 팀원의 비율 (0~1 사이의 실수)

active_hours: (활동 시간대, 비율)
- 활동 시간대: 프로젝트에 주로 시간을 언제 쏟는지를 나타냅니다. 
    "day": 낮에 활동하기를 선호해요.
    "night": 밤에 활동하기를 선호해요.
- 비율: 해당 시간대를 선호하는 팀원의 비율 (0~1 사이의 실수
)
meeting_preference: (미팅 방식, 비율)
- 미팅 방식: 선호하는 회의 방식입니다. 
    "online": 온라인으로 만나 회의하는 것을 선호합니다. 
    "offline": 오프라인으로 만나 회의하는 것을 선호합니다.
비율: 해당 미팅 방식을 선호하는 팀원의 비율 (0~1 사이의 실수)

ei, sn, tf, jp: 각 팀의 MBTI 지표의 평균값입니다. (0~1 사이의 실수)
0에 가까울수록 각각 e, s, t, j 성향에 가깝고, 1에 가까울수록 i, n, f, p 성향에 가깝습니다.

poppy_list: 팀원들의 devti(강아지 유형) 리스트
어떤 mbti가 어떤 강아지에 해당하는지는 devti_list.json 파일에서 확인할 수 있습니다.

wagging_pairs: 팀에서 누가 누구를 좋아하는지를 담은 리스트입니다. 
리스트 안에는 ["강아지1(파트)", "강아지2(파트)"] 같은 쌍이 들어있습니다. "강아지1"이 "강아지2"를 좋아한다는 뜻이고, 괄호 안에는 각 강아지의 파트(pm, de, fe, be)가 적혀있습니다.

팀 매칭이유 설명글 내용 예시1:
치와와, 도베르만, 시바견, 시고르자브종이 뛰어다니는 팀이네요!
이 팀은 다른 팀에 비해 E 성향이 강한 팀이에요.
낮에 활동하기를 좋아하고 배우면서 성장하기를 원하는 팀원들이 모이도록있게 매칭이 되었어요.
프론트의 치와와가 시바견을 좋아해요~ 서로 인사해보는건 어때요? 백엔드 파트의 도베르만도 시고르자브종이 마음에 드나봐요.

팀 매칭이유 설명글 내용 예시2:
보더콜리, 비글, 웰시코기, 푸들, 허스키가 뭉쳤네요.
이 팀은 다른 팀에 비해 T성향을 강하게 매칭되었어요.
밤에 활동하기를 좋아하고 전문적인 프로젝트를 원하는 팀원들이 모이도록 해봤어요.
푸들(백)이 보더콜리와 비글에 관심이 있었는데 같은 팀이 되이 되었네요. 팀플 열심히 해봐요!

팀 매칭이유 설명글 내용 예시3:
포메라니안, 진돗개, 사모예드, 그리고 허스키가 무려 3마리나 있네요!
이 팀은 다른 팀에 비해 P성향이 엄청 강하게 매칭되었어요.
밤에 활동하기를 좋아하는 팀원이 최대한 모이도록 매칭해봤어요. 빡센 분위기 보다는 차근차근 학습하는 분위기를 선호하는 팀이에요.
백엔드에 살고있는 허스키가 디자인 파트와 프론트 파트에 있는 허스키를 좋아해요. 사모예드끼리 즐겁게 공놀이라도 해봐요.

주의사항:
설명글은 공백 포함 300자 보다는 많게 작성해주세요. (약간의 이모지 사용도 허용)
team_info_list에 팀별로 팀 매칭 이유를 생성하여 "reason" 속성에 담아서 반환해주세요. 반드시 "reason" 속성만 추가해야하며, 다른 속성 값은 team_info_list의 값을 그대로 유지해주세요.
wagging(와깅), team_vibe, learning 등 코드에서 사용했던 단어는 설명글에 포함하지 말아줘.
백엔드의 푸들, 프론트의 사모예드와 같이 파트 이름까지 알려주는 표현은 똑같은 강아지들이 있어서 구별이 필요할 때 말고는 최대한 자제해줘.
자기자신에게 꼬리를 흔드는 것은 불가능해. 설명 생성에 주의해줘.


team_info_list = """

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
