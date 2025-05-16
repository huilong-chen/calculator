from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import LifestylePreferences, Match

User = get_user_model()

class LifestylePreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LifestylePreferences
        fields = [
            'smoking', 'smoking_preference',
            'drinking', 'drinking_preference',
            'exercise', 'exercise_preference',
            'work_life_balance', 'work_life_balance_preference'
        ]

class UserSerializer(serializers.ModelSerializer):
    lifestyle_preferences = LifestylePreferencesSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'gender', 'birth_date', 'bio', 'profile_picture',
            'lifestyle_preferences', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            gender=validated_data.get('gender', ''),
            birth_date=validated_data.get('birth_date', None),
            bio=validated_data.get('bio', '')
        )
        return user

class UserRegistrationSerializer(UserSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

class MatchSerializer(serializers.ModelSerializer):
    user1_details = UserSerializer(source='user1', read_only=True)
    user2_details = UserSerializer(source='user2', read_only=True)

    class Meta:
        model = Match
        fields = ['id', 'user1', 'user2', 'user1_details', 'user2_details', 
                 'compatibility_score', 'created_at']
        extra_kwargs = {
            'user1': {'write_only': True},
            'user2': {'write_only': True},
            'compatibility_score': {'read_only': True}
        }
