from dj_rest_auth.serializers import UserDetailsSerializer, TokenSerializer
from rest_framework import serializers


class CustomUserDetailsSerializer(UserDetailsSerializer):
    username = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        from ..models import User
        model = User
        fields = ("pk", "email", "username", "created_at")
        read_only_fields = ("email",)


class CustomTokenSerializer(TokenSerializer):
    user = CustomUserDetailsSerializer(read_only=True)

    class Meta(TokenSerializer.Meta):
        fields = TokenSerializer.Meta.fields + ("user",)
