from rest_framework.views import APIView
from rest_framework.response import Response
from matchings.models import Participant, Team, Member, Result, Room
from users.models import ProfilePM, ProfileDE, ProfileFE, ProfileBE
from django.db.models import Count, Q, Avg
import json


class DashboardAPIView(APIView):
    """
    관리자 대시보드용 데이터 반환 API (매칭룸 단위)
    """

    def get(self, request, room_id):
        # 매칭룸 존재 확인
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response(
                {
                    "status": "not found",
                    "code": 404,
                    "data": {},
                    "message": "매칭룸을 찾을 수 없습니다.",
                    "detail": None,
                },
                status=404,
            )

        # 해당 매칭룸의 전체 파트 분포
        part_dist_total = (
            Participant.objects.filter(room=room)
            .values("part")
            .annotate(count=Count("id"))
        )
        part_dist_total_dict = {p["part"]: p["count"] for p in part_dist_total}

        # 해당 매칭룸의 가장 최근 Result를 통해 팀 조회
        latest_result = Result.objects.filter(room=room).order_by("-id").first()
        if not latest_result:
            return Response(
                {
                    "status": "not found",
                    "code": 404,
                    "data": {},
                    "message": "매칭 결과가 존재하지 않습니다.",
                    "detail": None,
                },
                status=404,
            )
        teams = Team.objects.filter(result=latest_result).order_by("team_number")

        # 팀별 파트 분포
        part_dist = []
        for team in teams:
            members = Member.objects.filter(team=team).select_related("participant")
            part_count = {
                "team_number": team.team_number,
                "PM": 0,
                "DE": 0,
                "FE": 0,
                "BE": 0,
            }
            for m in members:
                part = m.participant.part
                if part in part_count:
                    part_count[part] += 1
            part_dist.append(part_count)

        # 팀별 프레임워크/언어 분포 (예시: FE/BE의 development_score 평균)
        framework_dist = []
        for team in teams:
            members = Member.objects.filter(team=team).select_related("participant")
            framework_scores = {}
            # FE
            fe_members = [m for m in members if m.participant.part == "FE"]
            for m in fe_members:
                try:
                    fe_profile = ProfileFE.objects.get(profile__user=m.participant.user)
                    dev_score = fe_profile.development_score
                    if dev_score:
                        # JSON 문자열인 경우 파싱
                        if isinstance(dev_score, str):
                            try:
                                dev_score = json.loads(dev_score)
                            except (json.JSONDecodeError, TypeError):
                                continue
                        # 리스트 형태인 경우 (예: [["react", 4.5], ["javascript", 4.0]])
                        if isinstance(dev_score, list):
                            for item in dev_score:
                                if isinstance(item, (list, tuple)) and len(item) >= 2:
                                    key, value = item[0], item[1]
                                    framework_scores[key] = framework_scores.get(key, 0) + float(value)
                        # 딕셔너리 형태인 경우
                        elif isinstance(dev_score, dict):
                            for k, v in dev_score.items():
                                framework_scores[k] = framework_scores.get(k, 0) + float(v)
                except ProfileFE.DoesNotExist:
                    continue
            # BE
            be_members = [m for m in members if m.participant.part == "BE"]
            for m in be_members:
                try:
                    be_profile = ProfileBE.objects.get(profile__user=m.participant.user)
                    dev_score = be_profile.development_score
                    if dev_score:
                        # JSON 문자열인 경우 파싱
                        if isinstance(dev_score, str):
                            try:
                                dev_score = json.loads(dev_score)
                            except (json.JSONDecodeError, TypeError):
                                continue
                        # 리스트 형태인 경우 (예: [["java", 4.5], ["springboot", 4.5]])
                        if isinstance(dev_score, list):
                            for item in dev_score:
                                if isinstance(item, (list, tuple)) and len(item) >= 2:
                                    key, value = item[0], item[1]
                                    framework_scores[key] = framework_scores.get(key, 0) + float(value)
                        # 딕셔너리 형태인 경우
                        elif isinstance(dev_score, dict):
                            for k, v in dev_score.items():
                                framework_scores[k] = framework_scores.get(k, 0) + float(v)
                except ProfileBE.DoesNotExist:
                    continue
            # 평균 계산 (단순 합산/멤버수로 나눔)
            total_members = len(fe_members) + len(be_members)
            if total_members > 0:
                for k in framework_scores:
                    framework_scores[k] = round(framework_scores[k] / total_members, 2)
            framework_dist.append(
                {"team_number": team.team_number, "framework_scores": framework_scores}
            )

        # 팀별 PM/디자인 역량 분포
        pm_design_dist = []
        for team in teams:
            members = Member.objects.filter(team=team).select_related("participant")
            pm_score = None
            pm_dev_score = None
            design_score = None
            # PM
            for m in members:
                if m.participant.part == "PM":
                    try:
                        pm_profile = ProfilePM.objects.get(
                            profile__user=m.participant.user
                        )
                        pm_score = pm_profile.design_understanding
                        pm_dev_score = pm_profile.development_understanding
                    except ProfilePM.DoesNotExist:
                        pass
                if m.participant.part == "DE":
                    try:
                        de_profile = ProfileDE.objects.get(
                            profile__user=m.participant.user
                        )
                        design_score = de_profile.design_score
                    except ProfileDE.DoesNotExist:
                        pass
            pm_design_dist.append(
                {
                    "team_number": team.team_number,
                    "pm_design_score": pm_score,
                    "pm_develop-score": pm_dev_score,
                    "design_score": design_score,
                }
            )

        data = {
            "part_dist_total": part_dist_total_dict,
            "part_dist": part_dist,
            "framework_dist": framework_dist,
            "pm_design_dist": pm_design_dist,
        }
        return Response(data)
