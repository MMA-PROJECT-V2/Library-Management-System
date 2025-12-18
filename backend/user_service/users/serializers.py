from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile, Permission, Group


# ============================================
#    USER SERIALIZERS
# ============================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name",
            "phone", "role", "is_active", "max_loans", "date_joined"
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user info including permissions (for token validation)"""
    permissions = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name",
            "phone", "role", "is_active", "max_loans", "date_joined",
            "is_staff", "is_superuser", "permissions", "groups"
        ]
    
    def get_permissions(self, obj):
        return obj.get_all_permissions_list()
    
    def get_groups(self, obj):
        return list(obj.custom_groups.values_list('name', flat=True))


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "username", "password", "first_name", "last_name", "phone", "role"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        
        # If role is provided, ensure we handle is_staff/is_superuser logic in create_user
        # But create_user in CustomUserManager doesn't automatically set is_staff based on role arg unless we modify it or handle it here.
        # Let's rely on the model's save method or handle it here if CustomUserManager is strict.
        
        # Checking CustomUserManager.create_user implementation again via view_file would be safe, 
        # but from previous context it took **extra_fields.
        
        user = User.objects.create_user(password=password, **validated_data)
        
        # Handle permission flags based on role
        if user.role == 'ADMIN':
            user.is_staff = True
            user.is_superuser = True
        elif user.role == 'LIBRARIAN':
            user.is_staff = True
            user.is_superuser = False
        else:
            user.is_staff = False
            user.is_superuser = False
        user.save()
        
        # Auto-assign to default group based on role
        from .models import Group
        default_group = Group.objects.filter(name=user.role).first()
        if default_group:
            user.custom_groups.add(default_group)
        
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
        if not user.is_active:
            raise serializers.ValidationError("Ce compte est désactivé.")
        
        attrs["user"] = user
        return attrs


# ============================================
#    TOKEN VALIDATION SERIALIZER (for introspection)
# ============================================

class TokenValidationResponseSerializer(serializers.Serializer):
    """Response format for token validation endpoint"""
    valid = serializers.BooleanField()
    user = UserDetailSerializer(required=False)
    error = serializers.CharField(required=False)


# ============================================
#    PROFILE SERIALIZERS
# ============================================

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["user", "bio", "address", "avatar_url", "birth_date"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["bio", "address", "avatar_url", "birth_date"]


# ============================================
#    PERMISSION & GROUP SERIALIZERS
# ============================================

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'code', 'name', 'description', 'category']


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True, write_only=True, source='permissions', required=False
    )
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'permissions', 'permission_ids', 'is_default']