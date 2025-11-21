from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, ParseError, NotFound
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *

@api_view(["GET"])
def participant_profile_view(request):
    return Response("응답 예시")


# 쿼리 파라미터와 해당 파트의 serializer/model/message를 매핑
PART_DISPATCHER = {
    'PM': {'serializer': ProfilePMCreateSerializer, 'model': ProfilePM, 'message': 'PM 프로필 생성 완료'},
    'FE': {'serializer': ProfileFECreateSerializer, 'model': ProfileFE, 'message': 'FE 프로필 생성 완료'},
    'BE': {'serializer': ProfileBECreateSerializer, 'model': ProfileBE, 'message': 'BE 프로필 생성 완료'},
    'DE': {'serializer': ProfileDECreateSerializer, 'model': ProfileDE, 'message': 'DE 프로필 생성 완료'},
}

class ProfileView(APIView):
    def get(self, request):
        return Response("응답 예시")

    def post(self, request):
        user = request.user
        part = request.query_params.get('part') # 쿼리 파라미터에서 part값 가져오기

        # 파라미터 값(part) 검사
        if not part or part not in PART_DISPATCHER:
            raise ParseError("part 쿼리 파라미터가 유요하지 않습니다. (허용 값: PM, FE, BE, DE)")
        
        # dispatcher에서 필요한 정보 추출
        dispatcher = PART_DISPATCHER[part]
        PartModel = dispatcher['model']
        PartSerializer = dispatcher['serializer']

        # 공통 Profile 가져오기 (소셜 로그인 시점에 생성)
        profile = get_object_or_404(Profile, user=user)
        
        # 이미 해당 part의 프로필이 존재하면 에러 발생 (이미 있으면 PUT 메서드로 수정만 가능)
        if PartModel.objects.filter(profile_id = profile).exists():
            raise ValidationError(f"이미 해당 파트({part})의 프로필이 존재합니다")

        # 데이터 유효성 검사
        serializer = PartSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        # DB에 저장
        serializer.save(profile_id=profile)
        
        # available_parts 목록 재생성(방금 생성된 파트가 포함된 최신 목록을 반환하기 위함)
        available_parts = []
        if ProfilePM.objects.filter(profile_id=profile).exists(): available_parts.append("PM")
        if ProfileFE.objects.filter(profile_id=profile).exists(): available_parts.append("FE")
        if ProfileBE.objects.filter(profile_id=profile).exists(): available_parts.append("BE")
        if ProfileDE.objects.filter(profile_id=profile).exists(): available_parts.append("DE")

        # response data 구성
        response_data = {
            "username": user.username,
            "email": user.email,
            "devti": profile.devti,
            "comment": profile.comment,
            "available_parts": available_parts,
            "part": part,
        }

        # 파트별 프로필 데이터 병합(response 값을 맞추기 위해)
        response_data.update(serializer.data)

        # message를 파트별로 구분해서 response_data에 추가 
        response_data['message'] = dispatcher['message']

        return Response(response_data, status=status.HTTP_201_CREATED)


    def put(self, request):
        return Response("응답 예시")


class DevtiView(APIView):

    def post(self, request):
        return Response("응답 예시")

    def put(self, request):
        return Response("응답 예시")
