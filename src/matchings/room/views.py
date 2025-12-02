from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound

from matchings.models import Room, Participant
from .serializers import (
    RoomCreateSerializer,
    RoomListSerializer,
    CodeValidationSerializer,
    AdminCodeValidationSerializer,
    RoomJoinSerializer
)
from ..utils import generate_unique_code, validate_room_entry


class RoomView(APIView):
    def get(self, request):
        """
        참여 중인 매칭룸 목록 조회
        """
        participants = Participant.objects.filter(user_id=request.user)
        serializer = RoomListSerializer(participants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        매칭룸 생성
        """
        serializer = RoomCreateSerializer(data=request.data)
        if serializer.is_valid():
            # 입장 코드 생성
            participant_code = generate_unique_code(6, "participant")
            admin_code = generate_unique_code(8, "admin")

            # 매칭룸 생성
            room = serializer.save(
                participant_code=participant_code,
                admin_code=admin_code,
                status=Room.Status.PENDING
            )

            # 매칭룸 생성자를 ADMIN 역할로 Participant 자동 생성
            Participant.objects.create(
                room_id=room,
                user_id=request.user,
                username=request.user.username,
                role=Participant.Role.ADMIN,
                part=None,
                team_vibe=None,
                active_hours=None,
                meeting_preference=None,
            )

            response_data = {
                "participant_code": room.participant_code,
                "admin_code": room.admin_code,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def validate_code_view(request):
    """
    참가자 입장 코드 검증
    """
    serializer = CodeValidationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    code = serializer.validated_data["participant_code"]
    user = request.user

    # 입장 코드 검증
    room = validate_room_entry(user, code, "participant")

    # 프로필 작성 여부 검증
    available_parts = user.available_parts
    if not available_parts:
        raise ValidationError("작성된 프로필이 없습니다.")

    return Response({
        "message": "참여 가능한 매칭룸",
        "room_id": room.id,
        "available_parts": available_parts,
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
def room_join_view(request):
    """
    참가자로 참여
    """
    serializer = RoomJoinSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    participant_code = serializer.validated_data["participant_code"]
    user = request.user

    # 입장 코드 검증
    room = validate_room_entry(user, participant_code, "participant")

    Participant.objects.create(
        room_id=room,
        user_id=user,
        username=user.username,
        role=Participant.Role.PARTICIPANT,
        part=serializer.validated_data["part"],
        team_vibe=serializer.validated_data["team_vibe"],
        active_hours=serializer.validated_data["active_hours"],
        meeting_preference=serializer.validated_data["meeting_preference"],
    )

    return Response({"message": "매칭룸 참여 완료"}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def room_join_admin_view(request):
    """
    운영진으로 참여
    """
    serializer = AdminCodeValidationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    code = serializer.validated_data["admin_code"]
    user = request.user

    # 입장 코드 검증
    room = validate_room_entry(user, code, "admin")

    Participant.objects.create(
        room_id=room,
        user_id=user,
        username=user.username,
        role=Participant.Role.ADMIN,
        part=None,
        team_vibe=None,
        active_hours=None,
        meeting_preference=None,
    )

    return Response({"message": "운영진 참여 완료"}, status=status.HTTP_201_CREATED)
