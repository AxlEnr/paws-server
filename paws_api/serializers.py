from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email', 'password', 'first_name', 'last_name', 'phone', 'address']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.password = make_password(password) 
        user.save()
        return user

class FamilySerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Family
        fields = ['id', 'name', 'members', 'creation_date', 'codeFam']

class PetSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    vaccines_url = serializers.SerializerMethodField()
    pet_type_display = serializers.CharField(source='get_pet_type_display', read_only=True)

    class Meta:
        model = Pet
        fields = ['id', 'name', 'pet_type', 'pet_type_display', 'age', 'breed', 
                 'adoption_date', 'photo', 'photo_url', 'vaccines', 'vaccines_url', 'owner']
        read_only_fields = ('owner', 'photo_url', 'vaccines_url', 'pet_type_display')

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None

    def get_vaccines_url(self, obj):
        if obj.vaccines:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.vaccines.url)
            return obj.vaccines.url
        return None

class PostImageSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    pet_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PostImage
        fields = [
            'id', 
            'photo', 
            'photo_url',
            'author', 
            'author_name',
            'pet', 
            'pet_name',
            'family',
            'upload_date', 
            'visibility', 
            'caption',
            'post'
        ]
        read_only_fields = ['author', 'upload_date']
    
    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.photo.url)
        return None
    
    def get_author_name(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}"
    
    def get_pet_name(self, obj):
        return obj.pet.name if obj.pet else None
    
    def validate(self, data):
        # Validar que el usuario pertenezca a la familia si se especifica
        if 'family' in data and data['family']:
            if not data['family'].members.filter(id=self.context['request'].user.id).exists():
                raise serializers.ValidationError("No perteneces a esta familia")
        
        # Validar que la mascota pertenezca al usuario
        if 'pet' in data and data['pet']:
            if data['pet'].owner != self.context['request'].user:
                raise serializers.ValidationError("No eres el dueño de esta mascota")
        
        return data

class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'post_type', 'status', 'images']

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['id', 'user', 'pet', 'title', 'description', 'due_date', 'reminder_type', 'status']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'notification_type', 'is_read']

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'pet', 'activity', 'created_at', 'duration', 'activity_type']