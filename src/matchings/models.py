from django.db import models


# Create your models here.
class Participant(models.Model):
    """
    매칭 참가자 테이믈
    """

    room_id = models.ForeignKey("Room", on_delete=models.CASCADE)
    user_id = models.ForeignKey("users.User", on_delete=models.CASCADE)
    username = models.CharField(max_length=30)
    role = models.CharField(max_length=10)
    part = models.CharField(max_length=10)
    team_vibe = models.CharField(max_length=10)
    active_hours = models.CharField(max_length=10)
    meeting_preference = models.CharField(max_length=10)
    carrot = models.BooleanField(default=False)

    class Meta:
        db_table = "participant"


class Wagging(models.Model):
    """
    꼬리 흔들기 관계 테이블
    """

    # 꼬리를 흔든 주체
    wagger = models.ForeignKey(
        "Participant", related_name="my_wagging_list", on_delete=models.CASCADE
    )

    # 꼬리를 흔든 대상
    waggee = models.ForeignKey(
        "Participant", related_name="who_wagging_me", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "wagging"


class Room(models.Model):
    """
    매칭룸 테이블
    """

    room_name = models.CharField(max_length=30)
    participant_code = models.CharField(max_length=10)
    admin_code = models.CharField(max_length=10)
    matching_at = models.DateTimeField()
    status = models.CharField(max_length=30)
    carrot_count = models.IntegerField(default=0)

    class Meta:
        db_table = "room"


class Result(models.Model):
    """
    팀 매칭 결과 테이블
    """

    room_id = models.ForeignKey("Room", on_delete=models.CASCADE)

    class Meta:
        db_table = "result"


class Team(models.Model):
    """
    팀 명단 테이블
    """

    result_id = models.ForeignKey("Result", on_delete=models.CASCADE)
    team_number = models.IntegerField()

    class Meta:
        db_table = "team"


class Member(models.Model):
    """
    팀원 정보 테이블
    """

    team_id = models.ForeignKey("Team", on_delete=models.CASCADE)
    participant_id = models.ForeignKey("Participant", on_delete=models.CASCADE)

    class Meta:
        db_table = "member"
