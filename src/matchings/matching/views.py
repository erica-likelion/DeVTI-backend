from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotFound

from drf_yasg.utils import swagger_auto_schema

from .serializers import WaggingSerializer
from ..models import Wagging, Participant, Room


@api_view(["POST"])
def carrot_control_view(request, participant_id):
    participant = Participant.objects.filter(id=participant_id).first()

    # 존재하지 않는 참가자가 당근 흔들기 요청
    if not participant:
        return Response(
            data={
                "status": "not found",
                "code": 404,
                "data": {},
                "message": f"존재하지 않는 참가자입니다. id: {participant_id}",
                "detail": None,
            },
            status=200,
        )

    response_message = (
        "당근을 흔들었습니니다."
        if participant.carrot == False
        else "당근 흔들기를 멈췄습니다."
    )
    participant.carrot = not participant.carrot
    participant.save()
    return Response(
        data={
            "status": "success",
            "code": 200,
            "data": {},
            "message": response_message,
            "detail": None,
        },
        status=200,
    )


@swagger_auto_schema(method="POST", request_body=WaggingSerializer)
@api_view(["POST"])
def wagging_control_view(request):
    """ """
    serializer = WaggingSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # 자기자신에게 꼬리를 흔드는 경우 제외
    if serializer.validated_data["wagger"] == serializer.validated_data["waggee"]:
        return Response(
            data={
                "status": "bad request",
                "code": 400,
                "data": {},
                "message": "자기자신에게 꼬리를 흔들 수 없습니다.",
                "detail": None,
            },
            status=400,
        )

    saved_wagging = Wagging.objects.filter(
        wagger=serializer.validated_data["wagger"],
        waggee=serializer.validated_data["waggee"],
    ).first()

    # 꼬리흔들기가 활성화 -> 비활성화
    if saved_wagging:
        saved_wagging.delete()
        return Response(
            data={
                "status": "success",
                "code": 200,
                "data": response_data,
                "message": "꼬리 흔들기를 취소했습니다.",
                "detail": None,
            },
            status=200,
        )

    # 꼬리흔들기 비활성화 -> 활성화
    else:
        new_wagging = serializer.save()
        response_data = WaggingSerializer(new_wagging).data
        return Response(
            data={
                "status": "success",
                "code": 200,
                "data": response_data,
                "message": "꼬리 흔들기를 완료했습니다.",
                "detail": None,
            },
            status=200,
        )


class MatchingView(APIView):

    def get(self, request, room_id):
        pass
        return Response("응답 예시")

    def post(self, request, room_id):
        pass
        return Response("응답 예시")
