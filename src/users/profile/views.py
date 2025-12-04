from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, ParseError, NotFound
from django.shortcuts import get_object_or_404
from django.db import transaction
from users.models import *
from matchings.models import Participant
from .serializers import *

# 쿼리 파라미터와 해당 파트의 serializer/model/message를 매핑
PART_DISPATCHER = {
    'PM': {'serializer': ProfilePMSerializer, 'model': ProfilePM, 'message': 'PM 프로필 생성 완료'},
    'FE': {'serializer': ProfileFESerializer, 'model': ProfileFE, 'message': 'FE 프로필 생성 완료'},
    'BE': {'serializer': ProfileBESerializer, 'model': ProfileBE, 'message': 'BE 프로필 생성 완료'},
    'DE': {'serializer': ProfileDESerializer, 'model': ProfileDE, 'message': 'DE 프로필 생성 완료'},
}

@api_view(["GET"])
def participant_profile_view(request,participant_id):
    # 참가자 객체 조회
    participant = get_object_or_404(Participant, id=participant_id)
    
    # 참가자의 해당 매칭에서의 파트 확인
    part = participant.part

    if part not in PART_DISPATCHER:
        raise ParseError(f"참가자의 파트 정보({part})가 유효하지 않습니다.")

    # 파트에 맞는 Serializer, Model 가져오기
    dispatcher = PART_DISPATCHER[part]
    PartModel = dispatcher['model']
    PartSerializer = dispatcher['serializer']

    # 참가자의 유저 프로필 찾기
    target_user = participant.user_id

    # 공통 프로필 & 파트별 상세 프로필 가져오기
    common_profile = get_object_or_404(Profile, user_id=target_user)

    try:
        part_profile = PartModel.objects.get(profile_id=common_profile)
    except PartModel.DoesNotExist:
        raise NotFound("참가자의 상세 프로필 정보가 존재하지 않습니다.")
    
    # pr 정보
    pr_data = ParticipantPRSerializer(participant).data

    # 공통 프로필 + 파트 프로필
    profile_data = {
        "id": common_profile.id,
        "devti": common_profile.devti,
        "comment": common_profile.comment,
        "part": part,
    }
    part_serializer = PartSerializer(part_profile)
    profile_data.update(part_serializer.data)

    # 최종 응답 데이터 구성(pr+프로필)
    response_data = {
        "pr": pr_data,
        "profile": profile_data,
        "message": f"id: {participant_id}번 {participant.username} 프로필 조회"
    }

    return Response(response_data, status=status.HTTP_200_OK)


class ProfileView(APIView):
    def get(self, request):
        user = request.user
        part = request.query_params.get('part')

        # 공통 프로필 가져오기
        profile = get_object_or_404(Profile, user_id=user)
        
        # available_parts 목록 계산
        available_parts = []
        if ProfilePM.objects.filter(profile_id=profile).exists(): available_parts.append("PM")
        if ProfileFE.objects.filter(profile_id=profile).exists(): available_parts.append("FE")
        if ProfileBE.objects.filter(profile_id=profile).exists(): available_parts.append("BE")
        if ProfileDE.objects.filter(profile_id=profile).exists(): available_parts.append("DE")
         
         # 기본 응답 데이터 구성
        response_data = {
            "username": user.username,
            "email": user.email,
            "devti": profile.devti,
            "comment": profile.comment,
            "available_parts": available_parts,
            "part": part, #파라미터에 없으면 None
         }
        
        # 분기 처리
        if not part:
            # 파라미터가 없는 경우(= 공통 프로필 조회인 경우)
            message = "공통 프로필 조회 완료"

        else:
            # 파라미터에 파트 있는 경우(= 파트별 조회인 경우)
            if part not in PART_DISPATCHER:
                raise ParseError("part 쿼리 파라미터가 유요하지 않습니다. (허용 값: PM, FE, BE, DE)")
            
            dispatcher = PART_DISPATCHER[part]
            PartModel = dispatcher['model']
            PartSerializer = dispatcher['serializer']

            # 해당 파트 프로필이 작성되어 있는지 확인
            try:
                part_instance = PartModel.objects.get(profile_id=profile)
            except PartModel.DoesNotExist:
                raise NotFound(f"해당 파트({part})의 프로필 데이터가 없습니다.")
            
            serializer = PartSerializer(part_instance)

            response_data.update(serializer.data)
            message = f"{part} 프로필 조회 완료"

        response_data['message'] = message
        return Response(response_data, status=status.HTTP_200_OK)

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

        # 공통 프로필 가져오기
        profile = get_object_or_404(Profile, user_id=user)
        
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
        user = request.user
        part = request.query_params.get('part')

        # 공통 프로필 가져오기
        profile = get_object_or_404(Profile, user_id=user)
        
        # 수정 로직
        # Profile과 User 두 테이블을 건드리기 때문에 트랜잭션 사용
        try:
            with transaction.atomic():
                if not part: # part 파라미터가 없는 경우(공통 프로필 수정)
                    if 'username' in request.data:
                        user.username = request.data['username']
                        user.save()
                    if 'comment' in request.data:
                        profile.comment = request.data['comment']
                        profile.save()
                    message = "공통 프로필 수정 완료"
                    part_data = {} # 공통 프로필 수정은 별도의 파트 데이터가 없음
                
                else: # part 파라미터가 있는 경우(파트별 프로필 수정)
                    if part not in PART_DISPATCHER:
                        raise ParseError("part 쿼리 파라미터가 유효하지 않습니다. (허용 값: PM, FE, BE, DE)")
                    
                    dispatcher = PART_DISPATCHER[part]
                    PartModel = dispatcher['model']
                    PartSerializer = dispatcher['serializer']

                    # 수정할 파트 데이터 찾기
                    try:
                        part_instance = PartModel.objects.get(profile_id=profile)
                    except PartModel.DoesNotExist:
                        raise NotFound(f"해당 파트({part})의 프로필이 존재하지 않습니다. (POST로 생성 필요)")
                    
                    serializer = PartSerializer(part_instance, data=request.data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    message = f"{part} 프로필 수정 완료"
                    part_data = serializer.data # 수정한 part_data 응답에 추가로 넘기기 위해 변수에 담아놓기

        except Exception as e:
            raise e
        
        # 최종 응답 데이터
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
            "part": part
        }

        # 파트별 수정이라면 그 데이터(part_data)까지 response_data에 병합
        if part:
            response_data.update(part_data)
        
        response_data['message'] = message

        return Response(response_data, status=status.HTTP_200_OK)


class DevtiView(APIView):

    def post(self, request):
        return self.process_devti(request)

    def put(self, request):
        return self.process_devti(request)
    
    def process_devti(self, request):
        # post, put 공통 로직 처리 메서드 
        user = request.user

        # 프로필 가져오기
        profile = get_object_or_404(Profile, user_id=user)

        # 받은 데이터 유효성 검사 
        serializer = DevtiTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 답변 리스트 추출 
        answers = serializer.validated_data['answers']

        # devti 결과 계산 함수에 넣어서 값 받아오기
        new_devti = self.calculate_devti(answers)

        # devti 업데이트/저장
        profile.devti = new_devti
        profile.save()

        # response_data 구성
        response_data = {
            "username": user.username,
            "devti": profile.devti,
            "message": "devti result saved"
        }

        # status_code 판별 (post면 201, put이면 200)
        if request.method == 'POST':
            status_code = status.HTTP_201_CREATED
        else:
            status_code = status.HTTP_200_OK

        return Response(response_data, status=status_code)

    def calculate_devti(self, answers):
        """
        추후에 질문 정해지면 devti 정해서 반환하는 함수 (현재는 임시 devti 반환만)
        """
        return "test_devti"

