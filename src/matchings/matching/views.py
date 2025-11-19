from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["POST"])
def carrot_control_view(request):
    pass
    return Response("응답 예시")


@api_view(["POST"])
def wagging_control_view(request):
    pass
    return Response("응답 예시")


class MatchingView(APIView):

    def get(self, request, room_id):
        pass
        return Response("응답 예시")

    def post(self, request, room_id):
        pass
        return Response("응답 예시")
