from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import LifestylePreferences, Match
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    LifestylePreferencesSerializer, MatchSerializer
)
import math

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class LifestylePreferencesViewSet(viewsets.ModelViewSet):
    serializer_class = LifestylePreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LifestylePreferences.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Match.objects.filter(Q(user1=user) | Q(user2=user))

    def calculate_compatibility(self, preferences1, preferences2):
        """Calculate compatibility score between two users based on their preferences"""
        
        weights = {
            'smoking': 0.3,
            'drinking': 0.3,
            'exercise': 0.2,
            'work_life_balance': 0.2
        }
        
        total_score = 0
        
        # Calculate smoking compatibility
        smoking_diff = abs(preferences1.smoking - preferences2.smoking_preference)
        smoking_score = 1 - (smoking_diff / 4)  # Normalize to 0-1 range
        total_score += smoking_score * weights['smoking']
        
        # Calculate drinking compatibility
        drinking_diff = abs(preferences1.drinking - preferences2.drinking_preference)
        drinking_score = 1 - (drinking_diff / 4)
        total_score += drinking_score * weights['drinking']
        
        # Calculate exercise compatibility
        exercise_diff = abs(preferences1.exercise - preferences2.exercise_preference)
        exercise_score = 1 - (exercise_diff / 4)
        total_score += exercise_score * weights['exercise']
        
        # Calculate work-life balance compatibility
        wlb_diff = abs(preferences1.work_life_balance - preferences2.work_life_balance_preference)
        wlb_score = 1 - (wlb_diff / 4)
        total_score += wlb_score * weights['work_life_balance']
        
        return total_score * 100  # Convert to percentage

    @action(detail=False, methods=['get'])
    def potential_matches(self, request):
        """Get potential matches for the current user"""
        user = request.user
        
        try:
            user_preferences = user.lifestyle_preferences
        except LifestylePreferences.DoesNotExist:
            return Response(
                {'error': 'Please set your lifestyle preferences first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all users except current user
        potential_matches = User.objects.exclude(id=user.id)
        matches = []
        
        for potential_match in potential_matches:
            try:
                match_preferences = potential_match.lifestyle_preferences
                
                # Calculate compatibility scores in both directions
                score1 = self.calculate_compatibility(user_preferences, match_preferences)
                score2 = self.calculate_compatibility(match_preferences, user_preferences)
                
                # Use average of both scores
                compatibility_score = (score1 + score2) / 2
                
                if compatibility_score >= 60:  # Only include matches with >60% compatibility
                    matches.append({
                        'user': UserSerializer(potential_match).data,
                        'compatibility_score': compatibility_score
                    })
            
            except LifestylePreferences.DoesNotExist:
                continue
        
        # Sort by compatibility score
        matches.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        return Response(matches)
