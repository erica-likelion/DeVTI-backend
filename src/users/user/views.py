from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404

from matchings.models import Room, Result, Team, Member
from .serializers import CarrotUsersResponseSerializer


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

    return Response(serializer.data, status=status.HTTP_200_OK)
