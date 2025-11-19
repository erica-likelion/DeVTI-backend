from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    """
    커스텀 유저 모델 정의
    """

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField()

    USERNAME_FIELD = "username"

    class Meta:
        db_table = "user"


class Profile(models.Model):
    """
    공통 프로필
    """

    user_id = models.ForeignKey("User", on_delete=models.CASCADE)
    devti = models.CharField(max_length=10, null=True)
    comment = models.TextField(null=True)

    class Meta:
        db_table = "profile"


class ProfilePM(models.Model):
    """
    PM 프로필
    """

    profile_id = models.ForeignKey(Profile, on_delete=models.CASCADE)
    experienced = models.TextField(null=True)  # "신입" 선택 시 null
    strength = models.TextField(null=True)
    daily_time_capacity = models.IntegerField(null=True)
    weekly_time_capacity = models.IntegerField(null=True)
    design_understanding = models.IntegerField(null=True)
    development_understanding = models.IntegerField(null=True)

    class Meta:
        db_table = "profile_pm"


class ProfileFE(models.Model):
    """
    프론트엔드 프로필
    """

    profile_id = models.ForeignKey(Profile, on_delete=models.CASCADE)
    experienced = models.TextField(null=True)  # "신입" 선택 시 null
    strength = models.TextField(null=True)
    github_url = models.URLField(max_length=200, null=True)
    development_score = models.CharField(max_length=30, null=True)

    class Meta:
        db_table = "profile_fe"


class ProfileBE(models.Model):
    """
    백엔드 프로필
    """

    profile_id = models.ForeignKey(Profile, on_delete=models.CASCADE)
    experienced = models.TextField(null=True)  # "신입" 선택 시 null
    strength = models.TextField(null=True)
    github_url = models.URLField(max_length=200, null=True)
    development_score = models.CharField(max_length=30, null=True)

    class Meta:
        db_table = "profile_be"


class ProfileDE(models.Model):
    """
    디자인 프로필
    """

    profile_id = models.ForeignKey(Profile, on_delete=models.CASCADE)
    experienced = models.TextField(null=True)  # "신입" 선택 시 null
    strength = models.TextField(null=True)
    portfolio_url = models.FileField(max_length=100, null=True)
    design_score = models.IntegerField(null=True)

    class Meta:
        db_table = "profile_de"
