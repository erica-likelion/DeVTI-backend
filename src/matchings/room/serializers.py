from rest_framework import serializers
from matchings.models import Room, Participant


class RoomCreateSerializer(serializers.ModelSerializer):
    """
    매칭룸 생성 시리얼라이저
    """
    class Meta:
        model = Room
        fields = ("room_name", "matching_at")


class RoomListSerializer(serializers.ModelSerializer):
    """
    참여 중인 매칭룸 목록 조회 시리얼라이저
    """
    id = serializers.IntegerField(source="room_id.id", read_only=True)
    name = serializers.CharField(source="room_id.room_name", read_only=True)
    status = serializers.CharField(source="room_id.status", read_only=True)

    class Meta:
        model = Participant
        fields = ("id", "name", "role", "status")


class RoomJoinSerializer(serializers.Serializer):
    """
    참가자 생성 시리얼라이저
    """
    participant_code = serializers.CharField(max_length=10)
    part = serializers.CharField(max_length=10)
    team_vibe = serializers.CharField(max_length=10)
    active_hours = serializers.CharField(max_length=10)
    meeting_preference = serializers.CharField(max_length=10)


class CodeValidationSerializer(serializers.Serializer):
    """
    참가자 입장 코드 검증 시리얼라이저
    """
    participant_code = serializers.CharField(max_length=10)


class AdminCodeValidationSerializer(serializers.Serializer):
    """
    운영진 입장 코드 검증 시리얼라이저
    """
    admin_code = serializers.CharField(max_length=10)
