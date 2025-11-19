from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response


from .models import User, UserProfile
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    LoginSerializer
)

# ======================
#    🔹 REGISTER
# ======================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response({
        "message": "Inscription réussie.",
        "user": UserSerializer(user).data
    })

# ======================
#     🔹 LOGIN
# ======================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Identifiants invalides."}, status=400)
    if not user.check_password(password):
        return Response({"error": "Identifiants invalides."}, status=400)
    return Response({
        "message": "Connexion réussie.",
        "user": UserSerializer(user).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Me(request):
    return Response({
        "user": UserSerializer(request.user).data
    })


@api_view(['GET' , 'PUT'])
@permission_classes([IsAuthenticated])
def UserProfileView(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)