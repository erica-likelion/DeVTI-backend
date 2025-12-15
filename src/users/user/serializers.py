from rest_framework import serializers
from matchings.models import Participant, Team, Member


class CarrotMemberSerializer(serializers.ModelSerializer):
    """
    당근을 흔든 팀원 정보 Serializer
    """

    participant_id = serializers.IntegerField(source="participant.id")
    participant_name = serializers.CharField(source="participant.username")
    part = serializers.CharField(source="participant.part")
    team_vibe = serializers.CharField(source="participant.team_vibe")
    active_hours = serializers.CharField(source="participant.active_hours")
    meeting_preference = serializers.CharField(source="participant.meeting_preference")

    class Meta:
        model = Member
        fields = [
            "participant_id",
            "participant_name",
            "part",
            "team_vibe",
            "active_hours",
            "meeting_preference",
        ]


class CarrotTeamSerializer(serializers.ModelSerializer):
    """
    당근을 흔든 사람들이 있는 팀 정보 Serializer
    """

    ai_description = serializers.CharField(source="explanation")
    members = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ["team_number", "ai_description", "members"]

    def get_members(self, obj):
        # 해당 팀의 멤버 중 당근을 흔든 사람만 필터링
        carrot_members = Member.objects.filter(
            team=obj, participant__carrot=True
        ).select_related("participant")
        return CarrotMemberSerializer(carrot_members, many=True).data


class CarrotUsersResponseSerializer(serializers.Serializer):
    """
    당근을 흔든 사용자 정보 전체 응답 Serializer
    """

    rematching_count = serializers.IntegerField()
    carrot_info = CarrotTeamSerializer(many=True)
