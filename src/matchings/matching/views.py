from .tasks import run_matching_task
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from drf_yasg.utils import swagger_auto_schema

from .serializers import WaggingSerializer, MatchingResultSerializer
from ..models import Wagging, Participant, Room, Team, Result, Member

from .simulated_annealing import random_team_assignment, simulated_annealing
from .explain import get_matching_explanations


@api_view(["POST"])
def carrot_control_view(request, participant_id):
    participant = Participant.objects.filter(id=participant_id).first()

    # 존재하지 않는 참가자가 당근 흔들기 요청
    if not participant:
        return Response(
            {"message": f"존재하지 않는 참가자입니다. id: {participant_id}"},
            status=404,
        )

    response_message = (
        "당근을 흔들었습니다."
        if not participant.carrot
        else "당근 흔들기를 멈췄습니다."
    )
    participant.carrot = not participant.carrot
    participant.save()

    # --- 웹소켓 브로드캐스트 시작 ---
    channel_layer = get_channel_layer()
    room_group_name = f"room_{participant.room.id}"

    # carrot.new 이벤트를 해당 방 그룹에 브로드캐스트
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            "type": "carrot.new",
            "payload": {
                "participant_id": participant.id,
            }
        },
    )
    # --- 웹소켓 브로드캐스트 종료 ---

    return Response({"message": response_message}, status=200)


@api_view(["POST"])
def wagging_start_view(request, room_id):
    user = request.user

    # 매칭룸 및 참가자 조회
    try:
        room = Room.objects.get(id=room_id)
        participant = Participant.objects.get(user=user, room=room)
    except Room.DoesNotExist:
        return Response(
            {"message": "매칭룸을 찾을 수 없습니다."},
            status=404,
        )
    except Participant.DoesNotExist:
        return Response(
            {"message": "해당 매칭룸의 참가자가 아닙니다."},
            status=403,
        )

    # 운영진 권한 확인
    if participant.role != Participant.Role.ADMIN:
        return Response(
            {"message": "운영진만 꼬리 흔들기를 시작할 수 있습니다."},
            status=403,
        )

    # 매칭룸 상태 변경
    room.status = Room.Status.WAGGING
    room.save()

    # 웹소켓 브로드캐스트
    channel_layer = get_channel_layer()
    room_group_name = f"room_{room_id}"
    event = {
        "type": "room_state_change",
        "payload": {
            "new_state": room.status,
        }
    }
    async_to_sync(channel_layer.group_send)(room_group_name, event)

    response_data = {
        "message": "꼬리 흔들기 상태로 변경되었습니다.",
        "room_id": room.id,
        "status": room.status
    }

    return Response(response_data, status=200)


@swagger_auto_schema(method="POST", request_body=WaggingSerializer)
@api_view(["POST"])
def wagging_control_view(request):
    """ """
    serializer = WaggingSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # 자기자신에게 꼬리를 흔드는 경우 제외
    if serializer.validated_data["wagger"] == serializer.validated_data["waggee"]:
        return Response({"message": "자기자신에게 꼬리를 흔들 수 없습니다."}, status=400)

    saved_wagging = Wagging.objects.filter(
        wagger=serializer.validated_data["wagger"],
        waggee=serializer.validated_data["waggee"],
    ).first()

    # 꼬리흔들기가 활성화 -> 비활성화
    if saved_wagging:
        saved_wagging.delete()
        return Response({"message": "꼬리 흔들기를 취소했습니다."}, status=200)
    # 꼬리흔들기 비활성화 -> 활성화
    else:
        new_wagging = serializer.save()
        response_data = WaggingSerializer(new_wagging).data
        return Response(
            {
                "message": "꼬리 흔들기를 완료했습니다.",
                **response_data
            },
            status=200
        )


class MatchingView(APIView):

    def get(self, request, room_id):
        try:
            matching_room = Room.objects.get(id=room_id)
            result = Result.objects.filter(room=matching_room).latest('id')
        except Room.DoesNotExist:
            return Response({"message": "매칭룸을 찾을 수 없습니다."}, status=404)
        except Result.DoesNotExist:
            return Response({"message": "매칭룸에 매칭 내역이 존재하지 않습니다."}, status=404)

        serializer = MatchingResultSerializer(result)
        return Response(
            {
                "message": "매칭 결과 조회 성공",
                **serializer.data
            },
            status=200
        )

    def post(self, request, room_id):
        user = request.user
        try:
            room = Room.objects.get(id=room_id)
            participant = Participant.objects.get(user=user, room=room)
        except Room.DoesNotExist:
            return Response({"message": "매칭룸을 찾을 수 없습니다."}, status=404)
        except Participant.DoesNotExist:
            return Response({"message": "해당 매칭룸의 참가자가 아닙니다."}, status=403)

        if participant.role != Participant.Role.ADMIN:
            return Response({"message": "운영진만 매칭을 시작할 수 있습니다."}, status=403)

        if room.status != Room.Status.COMPLETED:
            return Response({"message": f"현재 방 상태({room.status})에서는 리매칭을 시작할 수 없습니다."}, status=400)

        # MATCHING 상태로 변경하고 브로드캐스트
        room.status = Room.Status.MATCHING
        room.save()

        channel_layer = get_channel_layer()
        room_group_name = f"room_{room_id}"
        start_event = {
            "type": "room_state_change",
            "payload": {"new_state": room.status},
        }
        async_to_sync(channel_layer.group_send)(room_group_name, start_event)

        # Celery Task로 매칭 실행
        run_matching_task.delay(room.id)

        return Response({"message": "매칭 시작"}, status=202)


@api_view(["POST"])
def close_room_view(request, room_id):
    user = request.user

    # 매칭룸 및 참가자 조회
    try:
        room = Room.objects.get(id=room_id)
        participant = Participant.objects.get(user=user, room=room)
    except Room.DoesNotExist:
        return Response({"message": "매칭룸을 찾을 수 없습니다."}, status=404)
    except Participant.DoesNotExist:
        return Response({"message": "해당 매칭룸의 참가자가 아닙니다."}, status=403)

    # 운영진 권한 확인
    if participant.role != Participant.Role.ADMIN:
        return Response({"message": "운영진만 매칭 결과를 확정할 수 있습니다."}, status=403)

    # 매칭룸 상태가 COMPLETED인지 확인
    if room.status != Room.Status.COMPLETED:
        return Response({"message": f"현재 매칭룸 상태({room.status})에서는 매칭 결과를 확정할 수 없습니다."}, status=400)

    # 매칭룸 상태 변경 및 저장
    room.status = Room.Status.CLOSED
    room.save()

    # 웹소켓 브로드캐스트
    channel_layer = get_channel_layer()
    room_group_name = f"room_{room_id}"
    event = {
        "type": "room_state_change",
        "payload": {
            "new_state": room.status,
        }
    }
    async_to_sync(channel_layer.group_send)(room_group_name, event)

    response_data = {
        "message": "매칭 결과 확정 (status = CLOSED)",
        "room_id": room.id,
        "status": room.status
    }

    return Response(response_data, status=200)
