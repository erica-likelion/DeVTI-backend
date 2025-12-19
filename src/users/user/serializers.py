from rest_framework import serializers
from matchings.models import Participant, Team, Member, Wagging
from users.models import Profile, ProfilePM, ProfileFE, ProfileBE, ProfileDE


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


class ProfileDetailSerializer(serializers.Serializer):
    """
    프로필 상세 정보 Serializer (공통 프로필 + 파트별 프로필)
    """

    devti = serializers.CharField()
    comment = serializers.CharField()
    part = serializers.CharField()

    # PM 프로필 필드
    experienced = serializers.CharField(required=False, allow_null=True)
    strength = serializers.CharField(required=False, allow_null=True)
    daily_time_capacity = serializers.IntegerField(required=False, allow_null=True)
    weekly_time_capacity = serializers.IntegerField(required=False, allow_null=True)
    design_understanding = serializers.IntegerField(required=False, allow_null=True)
    development_understanding = serializers.IntegerField(
        required=False, allow_null=True
    )

    # FE/BE 프로필 필드
    github_url = serializers.URLField(required=False, allow_null=True)
    development_score = serializers.CharField(required=False, allow_null=True)

    # DE 프로필 필드
    portfolio_url = serializers.URLField(required=False, allow_null=True)
    design_score = serializers.IntegerField(required=False, allow_null=True)


class ParticipantWithProfileSerializer(serializers.ModelSerializer):
    """
    참가자 정보 + 프로필 + wagging 여부 Serializer
    """

    participant_id = serializers.IntegerField(source="id")
    participant_name = serializers.CharField(source="username")
    wagging = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = Participant
        fields = [
            "participant_id",
            "participant_name",
            "part",
            "team_vibe",
            "active_hours",
            "meeting_preference",
            "wagging",
            "profile",
        ]

    def get_wagging(self, obj):
        """
        요청한 사용자가 해당 참가자에게 꼬리를 흔들었는지 확인
        """
        request_user = self.context.get("request_user")
        if not request_user:
            return False

        # 요청한 사용자의 Participant 객체 찾기
        request_participant = self.context.get("request_participant")
        if not request_participant:
            return False

        # Wagging 관계 확인
        return Wagging.objects.filter(wagger=request_participant, waggee=obj).exists()

    def get_profile(self, obj):
        """
        참가자의 프로필 정보 가져오기 (공통 + 파트별)
        """
        try:
            # 참가자의 유저를 통해 프로필 가져오기
            user = obj.user
            profile = Profile.objects.get(user=user)

            # 기본 프로필 데이터
            profile_data = {
                "devti": profile.devti,
                "comment": profile.comment,
                "part": obj.part,  # 참가자의 파트
            }

            # 파트별 상세 프로필 추가
            part = obj.part
            if part == "PM":
                try:
                    part_profile = ProfilePM.objects.get(profile=profile)
                    profile_data.update(
                        {
                            "experienced": part_profile.experienced,
                            "strength": part_profile.strength,
                            "daily_time_capacity": part_profile.daily_time_capacity,
                            "weekly_time_capacity": part_profile.weekly_time_capacity,
                            "design_understanding": part_profile.design_understanding,
                            "development_understanding": part_profile.development_understanding,
                        }
                    )
                except ProfilePM.DoesNotExist:
                    pass
            elif part == "FE":
                try:
                    part_profile = ProfileFE.objects.get(profile=profile)
                    profile_data.update(
                        {
                            "experienced": part_profile.experienced,
                            "strength": part_profile.strength,
                            "github_url": part_profile.github_url,
                            "development_score": part_profile.development_score,
                        }
                    )
                except ProfileFE.DoesNotExist:
                    pass
            elif part == "BE":
                try:
                    part_profile = ProfileBE.objects.get(profile=profile)
                    profile_data.update(
                        {
                            "experienced": part_profile.experienced,
                            "strength": part_profile.strength,
                            "github_url": part_profile.github_url,
                            "development_score": part_profile.development_score,
                        }
                    )
                except ProfileBE.DoesNotExist:
                    pass
            elif part == "DE":
                try:
                    part_profile = ProfileDE.objects.get(profile=profile)
                    # ✅ 파일 객체를 URL 문자열로 변환
                    portfolio_url = None
                    if part_profile.portfolio_url:
                        try:
                            portfolio_url = part_profile.portfolio_url.url
                        except ValueError:
                            portfolio_url = None

                    profile_data.update(
                        {
                            "experienced": part_profile.experienced,
                            "strength": part_profile.strength,
                            "portfolio_url": portfolio_url,  # URL 문자열 또는 None
                            "design_score": part_profile.design_score,
                        }
                    )
                except ProfileDE.DoesNotExist:
                    pass

            return profile_data
        except Profile.DoesNotExist:
            return None


class RoomParticipantsResponseSerializer(serializers.Serializer):
    """
    매칭룸 참가자 목록 전체 응답 Serializer
    """

    recommend_reason = serializers.CharField()
    matching_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    participants = ParticipantWithProfileSerializer(many=True)
