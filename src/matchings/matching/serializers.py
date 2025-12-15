from rest_framework import serializers
from ..models import Wagging, Result, Team, Member, Participant
from users.models import Profile, ProfilePM, ProfileFE, ProfileBE, ProfileDE


class WaggingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wagging
        fields = "__all__"


class ParticipantPRSerializer(serializers.Serializer):
    """PR (Participant Room) 정보 시리얼라이저"""

    username = serializers.CharField()
    part = serializers.CharField()
    team_vibe = serializers.CharField()
    active_hours = serializers.CharField()
    meeting_preference = serializers.CharField()


class ProfileDataSerializer(serializers.Serializer):
    """프로필 상세 정보 시리얼라이저"""

    devti = serializers.CharField()
    comment = serializers.CharField()
    part = serializers.CharField()
    experienced = serializers.CharField(allow_null=True)
    strength = serializers.CharField(allow_null=True)
    daily_time_capacity = serializers.IntegerField(required=False, allow_null=True)
    weekly_time_capacity = serializers.IntegerField(required=False, allow_null=True)
    design_understanding = serializers.IntegerField(required=False, allow_null=True)
    development_understanding = serializers.IntegerField(
        required=False, allow_null=True
    )
    github_url = serializers.URLField(required=False, allow_null=True)
    development_score = serializers.CharField(required=False, allow_null=True)
    portfolio_url = serializers.CharField(required=False, allow_null=True)
    design_score = serializers.IntegerField(required=False, allow_null=True)


class TeamMemberSerializer(serializers.Serializer):
    """팀 멤버 정보 시리얼라이저"""

    id = serializers.IntegerField()
    pr = ParticipantPRSerializer()
    profile = ProfileDataSerializer()


class MatchingResultSerializer(serializers.Serializer):
    """매칭 결과 시리얼라이저"""

    def to_representation(self, instance):
        """
        Result 인스턴스를 받아서 팀별 멤버 정보를 반환
        """
        teams = Team.objects.filter(result=instance).order_by("team_number")
        result_data = []

        for team in teams:
            members = Member.objects.filter(team=team).select_related(
                "participant", "participant__user"
            )
            team_members = []

            for member in members:
                participant = member.participant
                user = participant.user

                # Profile 정보 가져오기
                try:
                    profile = Profile.objects.get(user_id=user)
                except Profile.DoesNotExist:
                    continue

                # PR (Participant Room) 정보
                pr_data = {
                    "username": participant.username,
                    "part": participant.part,
                    "team_vibe": participant.team_vibe,
                    "active_hours": participant.active_hours,
                    "meeting_preference": participant.meeting_preference,
                }

                # 파트별 프로필 정보 가져오기
                profile_data = {
                    "devti": profile.devti,
                    "comment": profile.comment,
                    "part": participant.part,
                }

                # 파트에 따라 추가 정보 가져오기
                if participant.part == "PM":
                    try:
                        profile_pm = ProfilePM.objects.get(profile_id=profile)
                        profile_data.update(
                            {
                                "experienced": profile_pm.experienced,
                                "strength": profile_pm.strength,
                                "daily_time_capacity": profile_pm.daily_time_capacity,
                                "weekly_time_capacity": profile_pm.weekly_time_capacity,
                                "design_understanding": profile_pm.design_understanding,
                                "development_understanding": profile_pm.development_understanding,
                            }
                        )
                    except ProfilePM.DoesNotExist:
                        pass

                elif participant.part == "FE":
                    try:
                        profile_fe = ProfileFE.objects.get(profile_id=profile)
                        profile_data.update(
                            {
                                "experienced": profile_fe.experienced,
                                "strength": profile_fe.strength,
                                "github_url": profile_fe.github_url,
                                "development_score": profile_fe.development_score,
                            }
                        )
                    except ProfileFE.DoesNotExist:
                        pass

                elif participant.part == "BE":
                    try:
                        profile_be = ProfileBE.objects.get(profile_id=profile)
                        profile_data.update(
                            {
                                "experienced": profile_be.experienced,
                                "strength": profile_be.strength,
                                "github_url": profile_be.github_url,
                                "development_score": profile_be.development_score,
                            }
                        )
                    except ProfileBE.DoesNotExist:
                        pass

                elif participant.part == "DE":
                    try:
                        profile_de = ProfileDE.objects.get(profile_id=profile)
                        profile_data.update(
                            {
                                "experienced": profile_de.experienced,
                                "strength": profile_de.strength,
                                "portfolio_url": (
                                    str(profile_de.portfolio_url)
                                    if profile_de.portfolio_url
                                    else None
                                ),
                                "design_score": profile_de.design_score,
                            }
                        )
                    except ProfileDE.DoesNotExist:
                        pass

                # 멤버 정보 조합
                team_members.append(
                    {
                        "id": participant.id,
                        "pr": pr_data,
                        "profile": profile_data,
                    }
                )

            result_data.append(team_members)

        return {"teams": result_data}
