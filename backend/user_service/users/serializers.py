from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile , Permission , Group


# -------------------------
# User Serializers
# -------------------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name",
            "last_name", "phone", "role", "is_active",
            "max_loans", "created_at", "updated_at"
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email", "username", "password",
            "first_name", "last_name", "phone"
        ]

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Le mot de passe doit contenir au moins 8 caractères."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(
            email=attrs.get("email"),
            password=attrs.get("password"),
        )
        if not user:
            raise serializers.ValidationError("Email ou mot de passe incorrect.")

        attrs["user"] = user
        return attrs


# -------------------------
# UserProfile Serializers
# -------------------------

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "bio",
            "address",
            "avatar_url",
            "birth_date",
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "bio",
            "address",
            "avatar_url",
            "birth_date",
        ]


# ============================================
#    PERMISSION SERIALIZERS
# ============================================

class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Permission model"""
    
    class Meta:
        model = Permission
        fields = ['id', 'code', 'name', 'description', 'category']
        read_only_fields = ['id']


class PermissionListSerializer(serializers.ModelSerializer):
    """Simplified permission serializer for lists"""
    
    class Meta:
        model = Permission
        fields = ['id', 'code', 'name', 'category']


# ============================================
#    GROUP SERIALIZERS
# ============================================

class GroupSerializer(serializers.ModelSerializer):
    """Full serializer for Group model"""
    
    permissions = PermissionListSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        source='permissions',
        required=False
    )
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = [
            'id', 'name', 'description', 'permissions', 
            'permission_ids', 'is_default', 'user_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_count(self, obj):
        return obj.users.count()


class GroupListSerializer(serializers.ModelSerializer):
    """Simplified group serializer for lists"""
    
    permission_count = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'is_default', 'permission_count', 'user_count']
    
    def get_permission_count(self, obj):
        return obj.permissions.count()
    
    def get_user_count(self, obj):
        return obj.users.count()


class GroupCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating groups"""
    
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=False
    )
    
    class Meta:
        model = Group
        fields = ['name', 'description', 'is_default', 'permission_ids']
    
    def create(self, validated_data):
        permissions = validated_data.pop('permission_ids', [])
        group = Group.objects.create(**validated_data)
        group.permissions.set(permissions)
        return group
    
    def update(self, instance, validated_data):
        permissions = validated_data.pop('permission_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if permissions is not None:
            instance.permissions.set(permissions)
        
        return instance

