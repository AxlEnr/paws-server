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
    class Meta:
        model = PostImage
        fields = ['id', 'post', 'url', 'image_type', 'upload_date']

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