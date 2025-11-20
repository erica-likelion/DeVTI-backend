from rest_framework import serializers
from .models import *

#PM post
class ProfilePMCreateSerializer(serializers.ModelSerializer):
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
class ProfileFECreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileFE
        fields = [
            'experienced',
            'strength',
            'github_url',
            'development_score'
        ]

#BE post
class ProfileBECreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileBE
        fields = [
            'experienced',
            'strength',
            'github_url',
            'development_score'
        ]

# DE post
class ProfileDECreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileDE
        fields = [
            'experienced', 
            'strength', 
            'portfolio_url', 
            'design_score'
        ]