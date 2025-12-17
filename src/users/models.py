from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


class UserManager(BaseUserManager):
    """
    커스텀 유저 매니저
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일 필드가 작성되어야 합니다.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    커스텀 유저 모델
    """

    username = models.CharField("사용자 이름", max_length=30)
    email = models.EmailField("이메일", unique=True)
    is_staff = models.BooleanField("관리자 권한", default=False)
    is_superuser = models.BooleanField("슈퍼유저 권한", default=False)
    is_active = models.BooleanField("활성 상태", default=True)
    created_at = models.DateTimeField("가입일", auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    class Meta:
        db_table = "user"

    def __str__(self):
        return self.email

    @property
    def available_parts(self):
        """
        작성 완료한 파트별 프로필 목록 반환
        """
        parts = []
        try:
            profile = self.profile_set.first()

            if hasattr(profile, "profilepm") and profile.profilepm is not None:
                parts.append("PM")
            if hasattr(profile, "profilefe") and profile.profilefe is not None:
                parts.append("FE")
            if hasattr(profile, "profilebe") and profile.profilebe is not None:
                parts.append("BE")
            if hasattr(profile, "profilede") and profile.profilede is not None:
                parts.append("DE")

            return parts

        except Exception:
            return []


class Profile(models.Model):
    """
    공통 프로필
    """

    user = models.ForeignKey("User", on_delete=models.CASCADE, db_column="user_id")
    devti = models.CharField(max_length=10, null=True)
    comment = models.TextField(null=True)
    ei = models.FloatField(null=True)
    sn = models.FloatField(null=True)
    tf = models.FloatField(null=True)
    jp = models.FloatField(null=True)

    class Meta:
        db_table = "profile"


class ProfilePM(models.Model):
    """
    PM 프로필
    """

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, db_column="profile_id"
    )
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

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, db_column="profile_id"
    )
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

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, db_column="profile_id"
    )
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

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, db_column="profile_id"
    )
    experienced = models.TextField(null=True)  # "신입" 선택 시 null
    strength = models.TextField(null=True)
    portfolio_url = models.FileField(max_length=100, null=True)
    design_score = models.IntegerField(null=True)

    class Meta:
        db_table = "profile_de"
