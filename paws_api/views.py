from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Family, Pet, Post, PostImage, Reminder, Notification, ActivityLog
from .serializers import *
from django.shortcuts import get_object_or_404
from django.utils import timezone
import logging
from rest_framework.views import APIView

# User Views
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_list(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Crear Usuario
@api_view(['POST'])
def signup_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# LOGIN Y GENERACIÓN DE TOKEN
logger = logging.getLogger(__name__)
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):  
                return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
            if not user.is_active:
                return Response({"error": "User is not active"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": user_data 
        }, status=status.HTTP_200_OK)

#OBTENER USUARIO DE LA SESIÓN ACTUAL
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_logged_in_user(request):
    try:
        user = request.user  
        if not user.is_active:
            return Response({"error": "User is inactive"}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error obteniendo usuario autenticado: {e}")
        return Response({"error": "Error interno del servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Family Views
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def family_list(request):
    if request.method == 'GET':
        families = Family.objects.filter(members=request.user)
        serializer = FamilySerializer(families, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data.copy()
        data['codeFam'] = generate_unique_family_code() 
        
        serializer = FamilySerializer(data=data)
        
        if serializer.is_valid():
            family = serializer.save()
            family.members.add(request.user)
            
            response_data = serializer.data
            response_data['codeFam'] = data['codeFam']
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

import string
import random
import secrets

def generate_unique_family_code():
    while True:
        code = generate_secure_code()
        if not Family.objects.filter(codeFam=code).exists():
            return code

def generate_secure_code():
    characters = string.ascii_letters + string.digits
    secure_str = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits)
    ]
    
    secure_str.extend(secrets.choice(characters) for _ in range(7))
    
    random.shuffle(secure_str)
    return ''.join(secure_str)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def family_detail(request, family_id):
    family = get_object_or_404(Family, id=family_id, members=request.user)
    
    if request.method == 'GET':
        serializer = FamilySerializer(family)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = FamilySerializer(family, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        family.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def family_add_member(request, family_id):
    family = get_object_or_404(Family, id=family_id, members=request.user)
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    family.members.add(user)
    return Response({'status': 'member added'}, status=status.HTTP_200_OK)

# Pet Views
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def pet_list(request):
    if request.method == 'GET':
        family_members = User.objects.filter(families__members=request.user).values_list('id', flat=True)
        pets = Pet.objects.filter(owner__in=[request.user.id] + list(family_members))
        serializer = PetSerializer(pets, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data.copy()
        data['owner'] = request.user.id
        serializer = PetSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def pet_detail(request, pet_id):
    family_members = User.objects.filter(families__members=request.user).values_list('id', flat=True)
    pet = get_object_or_404(Pet, id=pet_id, owner__in=[request.user.id] + list(family_members))
    
    if request.method == 'GET':
        serializer = PetSerializer(pet)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = PetSerializer(pet, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        pet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Post Views
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def post_list(request):
    if request.method == 'GET':
        # Obtener posts del usuario y de su familia
        family_members = User.objects.filter(families__members=request.user).values_list('id', flat=True)
        posts = Post.objects.filter(author__in=[request.user.id] + list(family_members))
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data.copy()
        data['author'] = request.user.id
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            post = serializer.save()
            
            # Manejar imágenes si vienen en la solicitud
            images = request.FILES.getlist('images')
            for image in images:
                PostImage.objects.create(post=post, image=image)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def post_detail(request, post_id):
    # Verificar que el post pertenezca al usuario o a su familia
    family_members = User.objects.filter(families__members=request.user).values_list('id', flat=True)
    post = get_object_or_404(Post, id=post_id, author__in=[request.user.id] + list(family_members))
    
    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Reminder Views
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def reminder_list(request):
    if request.method == 'GET':
        # Obtener recordatorios del usuario y de su familia
        family_members = User.objects.filter(families__members=request.user).values_list('id', flat=True)
        reminders = Reminder.objects.filter(user__in=[request.user.id] + list(family_members))
        serializer = ReminderSerializer(reminders, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = ReminderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def reminder_detail(request, reminder_id):
    # Verificar que el recordatorio pertenezca al usuario o a su familia
    family_members = User.objects.filter(families__members=request.user).values_list('id', flat=True)
    reminder = get_object_or_404(Reminder, id=reminder_id, user__in=[request.user.id] + list(family_members))
    
    if request.method == 'GET':
        serializer = ReminderSerializer(reminder)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ReminderSerializer(reminder, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        reminder.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Notification Views
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)

    if request.method == 'GET':
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = NotificationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return Response({'status': 'notification marked as read'}, status=status.HTTP_200_OK)

# ActivityLog Views
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def activity_log_list(request):
    if request.method == 'GET':
        # Obtener actividades del usuario y de su familia
        family_members = User.objects.filter(families__members=request.user).values_list('id', flat=True)
        activities = ActivityLog.objects.filter(user__in=[request.user.id] + list(family_members))
        serializer = ActivityLogSerializer(activities, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = ActivityLogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Special Endpoints
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_pet_with_post(request):
    # Crear mascota
    pet_data = request.data.copy()
    pet_data['owner'] = request.user.id
    pet_serializer = PetSerializer(data=pet_data)
    
    if not pet_serializer.is_valid():
        return Response(pet_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    pet = pet_serializer.save()
    
    # Crear post asociado
    post_data = {
        'author': request.user.id,
        'content': request.data.get('post_content', ''),
        'post_type': 'UPDATE'
    }
    post_serializer = PostSerializer(data=post_data)
    
    if not post_serializer.is_valid():
        pet.delete()  # Rollback si falla
        return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    post = post_serializer.save()
    
    return Response({
        'pet': pet_serializer.data,
        'post': post_serializer.data
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    # Datos resumidos para el dashboard del usuario
    pets_count = Pet.objects.filter(owner=request.user).count()
    reminders = Reminder.objects.filter(user=request.user, status='PENDING').order_by('due_date')[:5]
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:5]
    latest_posts = Post.objects.filter(author=request.user).order_by('-created_at')[:3]
    
    data = {
        'pets_count': pets_count,
        'pending_reminders': ReminderSerializer(reminders, many=True).data,
        'unread_notifications': NotificationSerializer(notifications, many=True).data,
        'latest_posts': PostSerializer(latest_posts, many=True).data
    }
    
    return Response(data)