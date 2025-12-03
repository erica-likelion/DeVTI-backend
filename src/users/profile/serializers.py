from rest_framework import serializers
from users.models import *

#PM post
class ProfilePMSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePM
        fields = [
            'experienced', 
            'strength', 
            'daily_time_capacity', 
            'weekly_time_capacity', 
            'design_understanding', 
            'development_understanding'
        ]

#FE post
class ProfileFESerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileFE
        fields = [
            'experienced',
            'strength',
            'github_url',
            'development_score'
        ]

#BE post
class ProfileBESerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileBE
        fields = [
            'experienced',
            'strength',
            'github_url',
            'development_score'
        ]

# DE post
class ProfileDESerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileDE
        fields = [
            'experienced', 
            'strength', 
            'portfolio_url', 
            'design_score'
        ]

# devti 
class DevtiTestSerializer(serializers.Serializer):
    answers = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=4), # 응답은 0-4로 고정
        min_length=28, 
        max_length=28, # min, max를 둘다 28로 한정해서 응답 수 28개로 고정
        allow_empty=False
    )