from rest_framework import serializers
from ..models import Wagging


class WaggingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wagging
        fields = "__all__"
