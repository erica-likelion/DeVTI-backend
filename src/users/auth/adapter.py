from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from users.models import Profile

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        data = sociallogin.account.extra_data
        username_candidate = None

        provider = sociallogin.account.provider.lower()
        if provider == "kakao":
            properties = data.get("properties", {})
            kakao_account = data.get("kakao_account", {})
            profile = kakao_account.get("profile", {})
            username_candidate = profile.get("nickname") or properties.get("nickname")
        elif provider == "google":
            username_candidate = data.get("name") or data.get("given_name")
        if not username_candidate:
            username_candidate = user.email.split("@")[0]

        user.username = username_candidate
        user.save()

        Profile.objects.create(user=user)

        return user
