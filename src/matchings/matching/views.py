from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotFound

from .serializers import WaggingSerializer
from ..models import Wagging


@api_view(["POST"])
def carrot_control_view(request):
    pass
    return Response("응답 예시")


@api_view(["POST"])
def wagging_control_view(request):
    """
    TODO:
        - wagging 데이터 수신 및 저장
        - wagging 테이블 중 동일한 wagger -> waggee 쌍이 생기지 않도록 에외 처리
    """
    active = request.query_params.get("active", None)

    if not active:  # query parameter 입력 없음
        return ParseError(
            detail="쿼리 파라미터 active를 전달해주세요. ?active=true || ?active=false"
        )

    active = True if active == "true" else False

    if active:  # 꼬리흔들기 추가
        serializer = WaggingSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        # 이미 존재하는 꼬리흔들기 내역인지 확인
        if Wagging.objects.filter(
            wagger=serializer.validated_data["wagger"],
            waggee=serializer.validated_data["waggee"],
        ).exists():
            raise ParseError(detail="이미 존재하는 꼬리흔들기 내역입니다.")

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

    else:  # 꼬리흔들기 취소
        wagging = Wagging.objects.filter(
            wagger=request.data["wagger"], waggee=request.data["waggee"]
        ).first()

        if not wagging:  # 취소할 꼬리흔들기 내역이 존재하지 않음
            raise NotFound(
                detail="꼬리 흔들기를 취소하지 못했습니다. (존재하지 않는 내역)"
            )

        wagging.delete()
        return Response(
            data={
                "status": "success",
                "code": 200,
                "data": response_data.data,
                "message": "꼬리 흔들기를 취소했습니다.",
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
