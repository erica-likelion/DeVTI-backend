from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs


@database_sync_to_async
def get_user_from_token_async(token_key):
    """
    비동기적으로 데이터베이스에서 토큰에 해당하는 사용자를 조회합니다.
    """
    try:
        token = Token.objects.select_related('user').get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    """
    쿼리 파라미터에서 토큰을 읽어 웹소켓 사용자를 인증하는 커스텀 미들웨어
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            query_string = scope.get("query_string", b"").decode("utf-8")
            query_params = parse_qs(query_string)
            token_key = query_params.get("token", [None])[0]

            if token_key:
                scope['user'] = await get_user_from_token_async(token_key)
            else:
                scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)
