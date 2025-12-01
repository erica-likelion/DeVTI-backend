from rest_framework.views import exception_handler
from rest_framework.renderers import JSONRenderer


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        status_code = response.status_code
        error_payload = response.data

        if isinstance(error_payload, dict) and "detail" in error_payload:
            message = error_payload["detail"]
        else:
            message = "입력값이 올바르지 않습니다."

        response.data = {
            "status": "error",
            "code": status_code,
            "data": None,
            "message": message,
            "detail": error_payload,
        }

    return response


class CustomRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context["response"]
        status_code = response.status_code

        if not str(status_code).startswith("2"):
            return super().render(data, accepted_media_type, renderer_context)

        message = None
        if isinstance(data, dict) and "message" in data:
            message = data.pop("message", None)

        response_data = {
            "status": "success",
            "code": status_code,
            "data": data,
            "message": message,
            "detail": None,
        }
        return super().render(response_data, accepted_media_type, renderer_context)
