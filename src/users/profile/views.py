from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *

@api_view(["GET"])
def participant_profile_view(request):
    return Response("응답 예시")


# 쿼리 파라미터와 해당 파트의 serializer/model을 연결
PART_DISPATCHER = {
    'PM': {'serializer': ProfilePMCreateSerializer, 'model': ProfilePM, 'message': 'PM 프로필 생성 완료'},
    'FE': {'serializer': ProfileFECreateSerializer, 'model': ProfileFE, 'message': 'FE 프로필 생성 완료'},
    'BE': {'serializer': ProfileBECreateSerializer, 'model': ProfileBE, 'message': 'BE 프로필 생성 완료'},
    'DE': {'serializer': ProfileDECreateSerializer, 'model': ProfileDE, 'message': 'DE 프로필 생성 완료'},
}
class ProfileView(APIView):
    # 로그인된 유저만 접근 가능
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response("응답 예시")

    def post(self, request):
        user = request.user
        part = request.query_params.get('part') # 쿼리 파라미터에서 part값 가져오기

        if not part or part not in PART_DISPATCHER:
            return Response(
                {"message" : "part 쿼리 파라미터가 유요하지 않습니다. (허용 값: PM, FE, BE, DE)"},
                status = status.HTTP_400_BAD_REQUEST
            )
        
        dispatcher = PART_DISPATCHER[part]
        PartModel = dispatcher['model']
        PartSerializer = dispatcher['serializer']

        # 공통 Profile 인스턴스 가져오기
        try:
            profile = Profile.objects.get(user_id=user)
        except Profile.DoesNotExist:
            return Response(
                {"message": "공통 프로필이 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND
            )
        
        if PartModel.objects.filter(profile_id = profile).exists():
            return Response(
                {"message": f"이미 해당 파트({part})의 프로필이 존재합니다."},
                status=status.HTTP_409_CONFLICT
            )

        serializer = PartSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        # DB에 저장
        try:
            with transaction.atomic():
                new_part_instance = serializer.save(profile_id = profile)
        except Exception as e:
            return Response(
                {"message": "DB 저장 중 오류 발생.", "error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # 새로운 파트가 추가되었으니 available_parts 목록 재생성
        available_parts = []
        if ProfilePM.objects.filter(profile_id=profile).exists(): available_parts.append("PM")
        if ProfileFE.objects.filter(profile_id=profile).exists(): available_parts.append("FE")
        if ProfileBE.objects.filter(profile_id=profile).exists(): available_parts.append("BE")
        if ProfileDE.objects.filter(profile_id=profile).exists(): available_parts.append("DE")

        response_data = {
            "username": user.username,
            "email": user.email,
            "devti": profile.devti,
            "comment": profile.comment,
            "available_parts": available_parts,
            "part": part,
        }

        # serializer의 결과를 합치기 (파트별 필드)
        response_data.update(serializer.data)

        final_response = {
            "status" : "success",
            "code" : status.HTTP_201_CREATED,
            "data": response_data,
            "message" : dispatcher['message']
        }

        return Response(final_response, status=status.HTTP_201_CREATED)


    def put(self, request):
        return Response("응답 예시")


class DevtiView(APIView):

    def post(self, request):
        return Response("응답 예시")

    def put(self, request):
        return Response("응답 예시")
