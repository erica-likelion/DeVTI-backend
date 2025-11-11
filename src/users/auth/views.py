from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(["POST"])
def register_view(request):
    return Response("응답 예시")


@api_view(["GET"])
def login_view(request):
    return Response("응답 예시")
