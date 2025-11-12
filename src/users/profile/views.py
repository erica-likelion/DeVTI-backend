from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def participant_profile_view(request):
    return Response("응답 예시")


class ProfileView(APIView):

    def get(self, request):
        return Response("응답 예시")

    def post(self, request):
        return Response("응답 예시")

    def put(self, request):
        return Response("응답 예시")


class DevtiView(APIView):

    def post(self, request):
        return Response("응답 예시")

    def put(self, request):
        return Response("응답 예시")
