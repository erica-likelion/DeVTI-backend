from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model

from matchings.models import Participant, Room
from .serializers import ParticipantDetailSerializer

User = get_user_model()


class RoomConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        '''
        웹소켓 연결이 시작될 때 호출되는 메서드
        '''

        # URL에서 room_id를 추출하고, 채널 그룹 이름을 설정
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"room_{self.room_id}"
        self.user = self.scope.get("user")

        # 사용자가 인증되었는지 확인
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # 사용자가 해당 매칭룸의 참가자가 맞는지 확인
        is_participant = await self.is_user_participant(self.user, self.room_id)
        if not is_participant:
            await self.close(code=4003)
            return

        # 채널 레이어의 그룹에 현재 채널(사용자)을 추가
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # 웹소켓 연결을 수락
        await self.accept()

        # 새로 연결된 클라이언트에게 현재 매칭룸의 참가자 목록을 전송
        await self.send_current_participants()

    async def disconnect(self, close_code):
        '''
        웹소켓 연결이 끊겼을 때 호출되는 메서드
        '''

        # 채널 레이어의 그룹에서 현재 채널을 제거
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content):
        '''
        클라이언트로부터 JSON 형식의 메시지를 받았을 때 호출되는 메서드
        '''

        # 현재 명세에 정의된 (클라이언트 -> 서버) 이벤트는 없으므로 비워 둠.
        pass

    @database_sync_to_async
    def is_user_participant(self, user, room_id):
        '''
        사용자가 해당 매칭룸의 참가자인지 확인
        '''
        try:
            room = Room.objects.get(id=room_id)
            return Participant.objects.filter(user=user, room=room).exists()
        except Room.DoesNotExist:
            return False

    @database_sync_to_async
    def get_room_participants_data(self):
        '''
        현재 매칭룸의 모든 참가자 목록을 반환
        '''
        try:
            room = Room.objects.get(id=self.room_id)
            participants = Participant.objects.filter(room=room, role=Participant.Role.PARTICIPANT)
            return ParticipantDetailSerializer(participants, many=True).data
        except Room.DoesNotExist:
            return []

    async def send_current_participants(self):
        '''
        현재 매칭룸의 모든 참가자 목록을 채널에 연결된 참가자에게 전송
        '''
        participants_data = await self.get_room_participants_data()
        await self.send_json({
            "type": "participants.list",
            "payload": {
                "participants": participants_data
            }
        })

    async def participant_new(self, event):
        '''
        participant.new 이벤트 핸들러
        '''
        await self.send_json(event)

    async def room_state_change(self, event):
        '''
        room.state_change 이벤트 핸들러
        '''
        await self.send_json(event)

    async def carrot_new(self, event):
        '''
        carrot.new 이벤트 핸들러
        '''
        await self.send_json(event)
