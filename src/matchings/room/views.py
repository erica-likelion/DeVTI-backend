from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["POST"])
def participate_view(request):
    return Response("응답 예시")


class RoomView(APIView):

    def get(self, reqeust):
        return Response("응답 예시")

    def post(self, request):
        return Response("응답 예시")
