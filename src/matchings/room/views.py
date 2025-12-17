from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from drf_yasg.utils import swagger_auto_schema

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from matchings.models import Room, Participant
from .serializers import (
    RoomCreateSerializer,
    RoomListSerializer,
    CodeValidationSerializer,
    AdminCodeValidationSerializer,
    ParticipantCreateSerializer,
    ParticipantDetailSerializer,
)
from ..utils import generate_unique_code, validate_room_entry


class RoomView(APIView):
    def get(self, request):
        """
        참여 중인 매칭룸 목록 조회
        """
        user = request.user
        participants = Participant.objects.filter(user=user)
        serializer = RoomListSerializer(participants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=RoomCreateSerializer)
    def post(self, request):
        """
        매칭룸 생성
        """
        serializer = RoomCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # 입장 코드 생성
            participant_code = generate_unique_code(6, "participant")
            admin_code = generate_unique_code(8, "admin")

            # 매칭룸 생성
            room = serializer.save(
                participant_code=participant_code,
                admin_code=admin_code,
                status=Room.Status.PENDING,
            )

            # 매칭룸 생성자를 ADMIN 역할로 Participant 자동 생성
            Participant.objects.create(
                room=room,
                user=user,
                username=user.username,
                role=Participant.Role.ADMIN,
                part="",
                team_vibe="",
                active_hours="",
                meeting_preference="",
                ei=0,
                sn=0,
                tf=0,
                jp=0,
            )

            response_data = {
                "participant_code": room.participant_code,
                "admin_code": room.admin_code,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomDetailView(APIView):
    def delete(self, request, room_id):
        """
        매칭룸 삭제
        """
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise NotFound("해당 매칭룸을 찾을 수 없습니다.")

        # 요청한 사용자가 해당 방의 ADMIN인지 확인
        is_admin = Participant.objects.filter(
            room=room, user=request.user, role=Participant.Role.ADMIN
        ).exists()

        if not is_admin:
            raise PermissionDenied("이 매칭룸을 삭제할 권한이 없습니다.")

        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method="POST", request_body=CodeValidationSerializer)
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

    return Response(
        {
            "message": "참여 가능한 매칭룸",
            "room_id": room.id,
            "available_parts": available_parts,
        },
        status=status.HTTP_200_OK,
    )


@swagger_auto_schema(method="POST", request_body=ParticipantCreateSerializer)
@api_view(["POST"])
def room_join_view(request):
    """
    참가자로 참여
    """
    serializer = ParticipantCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    participant_code = serializer.validated_data["participant_code"]
    user = request.user

    # 입장 코드 검증
    room = validate_room_entry(user, participant_code, "participant")

    # 프로필 가져오기
    profile = user.profile_set.first()

    # 참가자 객체 생성
    created_participant = Participant.objects.create(
        room=room,
        user=user,
        username=user.username,
        role=Participant.Role.PARTICIPANT,
        part=serializer.validated_data["part"],
        team_vibe=serializer.validated_data["team_vibe"],
        active_hours=serializer.validated_data["active_hours"],
        meeting_preference=serializer.validated_data["meeting_preference"],
        ei=profile.ei,
        sn=profile.sn,
        tf=profile.tf,
        jp=profile.jp,
    )

    # --- 웹소켓 브로드캐스트 시작 ---
    participant_data = ParticipantDetailSerializer(created_participant).data

    channel_layer = get_channel_layer()
    room_group_name = f"room_{room.id}"

    # participant.new 이벤트를 해당 방 그룹에 브로드캐스트
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            "type": "participant.new",
            "payload": participant_data,
        },
    )
    # --- 웹소켓 브로드캐스트 종료 ---

    return Response({"message": "매칭룸 참여 완료"}, status=status.HTTP_201_CREATED)


@swagger_auto_schema(method="POST", request_body=AdminCodeValidationSerializer)
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
        room=room,
        user=user,
        username=user.username,
        role=Participant.Role.ADMIN,
        part="",
        team_vibe="",
        active_hours="",
        meeting_preference="",
        ei=0,
        sn=0,
        tf=0,
        jp=0,
    )

    return Response({"message": "운영진 참여 완료"}, status=status.HTTP_201_CREATED)
