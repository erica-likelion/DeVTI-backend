from django.db import models


# Create your models here.
class Participant(models.Model):
    """
    매칭 참가자 테이블
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "운영진"
        PARTICIPANT = "PARTICIPANT", "참가자"

    room = models.ForeignKey("Room", on_delete=models.CASCADE, db_column="room_id")
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, db_column="user_id"
    )
    username = models.CharField(max_length=30)
    role = models.CharField(max_length=10)
    part = models.CharField(max_length=10)
    team_vibe = models.CharField(max_length=20)
    active_hours = models.CharField(max_length=10)
    meeting_preference = models.CharField(max_length=10)
    ei = models.FloatField()
    sn = models.FloatField()
    tf = models.FloatField()
    jp = models.FloatField()
    carrot = models.BooleanField(default=False)

    class Meta:
        db_table = "participant"


class Wagging(models.Model):
    """
    꼬리 흔들기 관계 테이블
    """

    # 꼬리를 흔든 주체
    wagger = models.ForeignKey(
        "Participant",
        related_name="my_wagging_list",
        on_delete=models.CASCADE,
        db_column="wagger_id",
    )

    # 꼬리를 흔든 대상
    waggee = models.ForeignKey(
        "Participant",
        related_name="who_wagging_me",
        on_delete=models.CASCADE,
        db_column="waggee_id",
    )

    class Meta:
        db_table = "wagging"


class Room(models.Model):
    """
    매칭룸 테이블
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "대기"
        WAGGING = "WAGGING", "꼬리 흔들기"
        MATCHING = "MATCHING", "매칭"
        COMPLETED = "COMPLETED", "완료"
        CLOSED = "CLOSED", "닫힘"

    room_name = models.CharField(max_length=30)
    participant_code = models.CharField(max_length=10)
    admin_code = models.CharField(max_length=10)
    matching_at = models.DateTimeField()
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.PENDING
    )
    carrot_count = models.IntegerField(default=0)
    wagging_start = models.BooleanField(default=False)

    class Meta:
        db_table = "room"


class Result(models.Model):
    """
    팀 매칭 결과 테이블
    """

    room = models.ForeignKey("Room", on_delete=models.CASCADE, db_column="room_id")

    class Meta:
        db_table = "result"


class Team(models.Model):
    """
    팀 명단 테이블
    """

    result = models.ForeignKey(
        "Result", on_delete=models.CASCADE, db_column="result_id"
    )
    team_number = models.IntegerField()
    explanation = models.TextField()

    class Meta:
        db_table = "team"


class Member(models.Model):
    """
    팀원 정보 테이블
    """

    team = models.ForeignKey("Team", on_delete=models.CASCADE, db_column="team_id")
    participant = models.ForeignKey(
        "Participant", on_delete=models.CASCADE, db_column="participant_id"
    )

    class Meta:
        db_table = "member"
