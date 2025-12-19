from config.celery import app as celery_app
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models import Participant, Room, Team, Result, Member, Wagging
from .simulated_annealing import random_team_assignment, simulated_annealing
from .explain import get_matching_explanations


@celery_app.task
def run_matching_task(room_id):
    """
    백그라운드에서 매칭 알고리즘을 실행하는 Celery Task.
    """
    try:
        matching_room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        print(f"ID가 {room_id}인 매칭룸이 존재하지 않아 매칭 Task를 건너뜁니다.")
        return

    room_group_name = f"room_{matching_room.id}"
    channel_layer = get_channel_layer()

    try:
        # 모든 참가자의 carrot 상태를 False로 초기화
        Participant.objects.filter(room=matching_room).update(carrot=False)

        participants = Participant.objects.filter(room=matching_room).select_related("user")
        participant_list = []
        participant_ids = []
        for p in participants:
            profile = getattr(p.user, "profile_set", None)
            if profile:
                profile = profile.first()
            participant_list.append({
                "id": p.id, "part": p.part, "team_vibe": p.team_vibe,
                "active_hours": p.active_hours, "meeting_preference": p.meeting_preference,
                "ei": profile.ei if profile else None, "sn": profile.sn if profile else None,
                "tf": profile.tf if profile else None, "jp": profile.jp if profile else None,
                "devti": profile.devti if profile else None,
            })
            participant_ids.append(p.id)

        waggings = list(
            Wagging.objects.filter(wagger__id__in=participant_ids).values(
                "wagger", "waggee"
            )
        )
        initial_team = random_team_assignment(participant_list)
        best_team_list, score = simulated_annealing(initial_team, waggings)
        explanations = get_matching_explanations(best_team_list, waggings)

        # 새로운 매칭 결과를 저장
        with transaction.atomic():
            result = Result.objects.create(room=matching_room)
            for i, team in enumerate(best_team_list):
                team_instance = Team.objects.create(
                    team_number=i + 1, result=result, explanation=explanations[i].reason
                )
                for member in team:
                    participant_obj = Participant.objects.get(id=member["id"])
                    Member.objects.create(team=team_instance, participant=participant_obj)

        # rematch_count를 1 증가
        matching_room.rematch_count += 1

        # rematch_count가 2 이상이면 Room의 상태를 CLOSED로, 그렇지 않으면 COMPLETED로 설정
        if matching_room.rematch_count >= 2:
            matching_room.status = Room.Status.CLOSED
        else:
            matching_room.status = Room.Status.COMPLETED
        matching_room.save()

        complete_event = {
            "type": "room_state_change",
            "payload": {"new_state": matching_room.status},
        }
        async_to_sync(channel_layer.group_send)(room_group_name, complete_event)

    except Exception as e:
        matching_room.status = Room.Status.PENDING
        matching_room.save()
        error_event = {
            "type": "room_state_change",
            "payload": {"new_state": matching_room.status, "error": f"매칭 과정에서 오류가 발생했습니다: {str(e)}"},
        }
        async_to_sync(channel_layer.group_send)(room_group_name, error_event)
