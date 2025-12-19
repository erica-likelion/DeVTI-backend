from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404

from matchings.models import Room, Result, Team, Member, Participant
from .serializers import (
    CarrotUsersResponseSerializer,
    RoomParticipantsResponseSerializer,
)


@api_view(["GET"])
def get_carrot_users(request, room_id):
    """
    당근을 흔든 참가자 정보 조회
    """
    # 매칭룸 존재 확인
    room = get_object_or_404(Room, id=room_id)

    # 해당 room의 최신 매칭 결과 가져오기
    result = Result.objects.filter(room=room).order_by("-id").first()

    if not result:
        raise NotFound("매칭 결과가 존재하지 않습니다.")

    # 리매칭 횟수 계산 (전체 결과 개수 - 1)
    rematching_count = Result.objects.filter(room=room).count() - 1

    # 당근을 흔든 멤버가 있는 팀들만 필터링
    teams_with_carrot = (
        Team.objects.filter(result=result)
        .prefetch_related("member_set__participant")
        .filter(member__participant__carrot=True)
        .distinct()
    )

    # 응답 데이터 구성
    response_data = {
        "rematching_count": rematching_count,
        "carrot_info": teams_with_carrot,
    }

    serializer = CarrotUsersResponseSerializer(response_data)

    return Response(
        {
            "status": "success",
            "code": 200,
            "data": serializer.data,
            "message": "carrot users fetched",
            "detail": None,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
def get_room_users(request, room_id):
    """
    매칭룸 참가자 목록 조회 (프로필 정보 포함)
    """
    # 매칭룸 존재 확인
    room = get_object_or_404(Room, id=room_id)

    # 요청한 사용자의 Participant 객체 찾기
    try:
        request_participant = Participant.objects.get(room=room, user=request.user)
    except Participant.DoesNotExist:
        raise NotFound("해당 매칭룸에 참여하지 않은 사용자입니다.")

    # 해당 룸의 참가자 목록 조회 (본인 제외)
    participants = (
        Participant.objects.filter(room=room)
        .exclude(id=request_participant.id)
        .select_related("user")
    )

    # Serializer에 context 전달 및 matching_at 추가
    serializer = RoomParticipantsResponseSerializer(
        {
            "recommend_reason": "매칭룸에 참여 중인 다른 참가자들입니다.",
            "matching_at": room.matching_at,
            "participants": participants,
        },
        context={
            "request_user": request.user,
            "request_participant": request_participant,
        },
    )

    return Response(
        {
            "status": "success",
            "code": 200,
            "data": serializer.data,
            "message": "room users fetched",
            "detail": None,
        },
        status=status.HTTP_200_OK,
    )
