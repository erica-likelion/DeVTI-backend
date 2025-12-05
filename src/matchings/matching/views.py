from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction

from drf_yasg.utils import swagger_auto_schema

from .serializers import WaggingSerializer, MatchingResultSerializer
from ..models import Wagging, Participant, Room, Team, Result, Member

from simulated_annealing import random_team_assignment, simulated_annealing
from explain import get_matching_explanations


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
            status=404,
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
            "status": "ok",
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
                "status": "ok",
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
                "status": "ok",
                "code": 200,
                "data": response_data,
                "message": "꼬리 흔들기를 완료했습니다.",
                "detail": None,
            },
            status=200,
        )


class MatchingView(APIView):

    def get(self, request, room_id):
        matching_room = Room.objects.filter(id=room_id).first()

        # 존재하지 않는 매칭룸을 요청
        if not matching_room:
            return Response(
                data={
                    "status": "not found",
                    "code": 404,
                    "data": {},
                    "message": "매칭룸을 찾을 수 없습니다.",
                    "detail": None,
                },
                status=404,
            )

        result = Result.objects.filter(room=matching_room).order_by("-id").first()

        # 아직 매칭 내역이 없을 때
        if not result:
            return Response(
                data={
                    "status": "not found",
                    "code": 404,
                    "data": {},
                    "message": "매칭룸에 매칭 내역이 존재하지 않습니다.",
                    "detail": None,
                },
                status=404,
            )

        serializer = MatchingResultSerializer(result)

        return Response(
            data={
                "status": "ok",
                "code": 200,
                "data": serializer.data,
                "message": "매칭 결과를 조회에 성공했습니다.",
                "detail": None,
            },
            status=200,
        )

    def post(self, request, room_id):
        matching_room = Room.objects.filter(id=room_id).first()

        # 존재하지 않는 매칭룸을 요청
        if not matching_room:
            return Response(
                data={
                    "status": "not found",
                    "code": 404,
                    "data": {},
                    "message": "매칭룸을 찾을 수 없습니다.",
                    "detail": None,
                },
                status=404,
            )
        participant_list = list(Participant.objects.filter(room=matching_room).values())
        participant_ids = participant_list.values_list("id", flat=True)
        waggings = list(Wagging.objects.filter(wagger__id__in=participant_ids).values())
        initial_team = random_team_assignment(participant_list)
        best_team_list, score = simulated_annealing(initial_team, waggings)
        explanations = get_matching_explanations(best_team_list, waggings)

        # 새로운 매칭 결과를 저장
        try:
            with transaction.atomic():
                result = Result.objects.create(room=matching_room)
                for i, team in enumerate(best_team_list):
                    team_instance = Team.objects.create(
                        team_number=i + 1, result=result, explanation=explanations[i]
                    )

                    for member in team:
                        Member.objects.create(team=team_instance, participant=member)
            serializer = MatchingResultSerializer(result)
            return Response(
                data={
                    "status": "ok",
                    "code": 200,
                    "data": serializer.data,
                    "message": "매칭이 완료되었습니다.",
                    "detail": None,
                },
                status=200,
            )

        except Exception as e:
            return Response(
                data={
                    "status": "internal server error",
                    "code": 500,
                    "data": {},
                    "message": "매칭 결과를 저장하는 과정에서 오류가 발생했습니다.",
                    "detail": str(e),
                },
                status=500,
            )
