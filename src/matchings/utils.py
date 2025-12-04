import random
import string

from rest_framework.exceptions import ValidationError, NotFound

from matchings.models import Room, Participant


def generate_unique_code(length=6, code_type="participant"):
    """
    입장 코드 생성
    """
    characters = string.ascii_uppercase + string.digits
    while True:
        code = "".join(random.choice(characters) for _ in range(length))
        if code_type == "participant":
            if not Room.objects.filter(participant_code=code).exists():
                break
        elif code_type == "admin":
            if not Room.objects.filter(admin_code=code).exists():
                break
        else:
            raise ValueError("code_type은 'participant' 또는 'admin' 중 하나여야 합니다.")
    return code


def validate_room_entry(user, code, code_type="participant"):
    """
    입장 코드 검증
    """
    code_lookup = {f"{code_type}_code": code}
    try:
        room = Room.objects.get(**code_lookup)
    except Room.DoesNotExist:
        raise NotFound("유효하지 않은 코드입니다.")

    if room.status != Room.Status.PENDING:
        raise ValidationError("참여 가능한 매칭룸이 아닙니다.")

    if Participant.objects.filter(room_id=room, user_id=user).exists():
        raise ValidationError("이미 참여 중인 매칭룸입니다.")

    return room
