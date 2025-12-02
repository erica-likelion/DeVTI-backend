import random
import string
from matchings.models import Room


def generate_unique_code(length=6, code_type="participant"):
    """
    고유한 입장 코드 생성.
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
