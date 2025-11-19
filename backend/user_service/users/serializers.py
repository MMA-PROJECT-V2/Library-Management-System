from rest_framework import serializers
from .models import User, UserProfile


# ---------------------------------------------------------
# User Serializers
# ---------------------------------------------------------

class UserSerializer(serializers.ModelSerializer):
    """Serializer pour renvoyer les infos utilisateur sans le mot de passe"""
    
    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name",
            "last_name", "phone", "role", "is_active",
            "max_loans", "created_at", "updated_at"
        ]

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer utilisé pour l'inscription"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email", "username", "password",
            "first_name", "last_name", "phone"
        ]

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

