from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    family_id = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'phone', 'address', 'family_id']
    
    def get_family_id(self, obj):
        family = obj.families.first()
        return family.id if family else None
    
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
                 'adoption_date', 'photo', 'photo_url', 'vaccines', 'vaccines_url', 'owner', 'family']
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
    author = serializers.PrimaryKeyRelatedField(read_only=True)  # Esto es importante
    images = PostImageSerializer(many=True, read_only=True)
    pet = PetSerializer(read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'created_at', 'post_type', 'status', 'images', 'pet']
        read_only_fields = ('author', 'created_at', 'status')

class ReminderSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False, 
        allow_null=True
    )
    pet = serializers.PrimaryKeyRelatedField(
        queryset=Pet.objects.all(), 
        required=False, 
        allow_null=True
    )
    
    class Meta:
        model = Reminder
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def validate(self, data):
        user = self.context['request'].user
        family = user.families.first()
        
        # Validar mascota
        if 'pet' in data and data['pet']:
            if data['pet'].owner != user and (not family or data['pet'].family != family):
                raise serializers.ValidationError(
                    {"pet": "No tienes permisos sobre esta mascota"}
                )
        
        # Validar miembro de familia
        if 'assigned_to' in data and data['assigned_to']:
            if not family or not family.members.filter(id=data['assigned_to'].id).exists():
                raise serializers.ValidationError(
                    {"assigned_to": "Este usuario no pertenece a tu familia"}
                )
        
        # Validar familia
        if 'family' in data and data['family']:
            if data['family'] != family:
                raise serializers.ValidationError(
                    {"family": "No tienes permisos sobre esta familia"}
                )
        
        # Validar repetición
        if data.get('is_recurring', False):
            if not data.get('recurrence_type') or data['recurrence_type'] == 'NONE':
                raise serializers.ValidationError(
                    {"recurrence_type": "Debe seleccionar un tipo de repetición"}
                )
            if not data.get('recurrence_value') or data['recurrence_value'] < 1:
                raise serializers.ValidationError(
                    {"recurrence_value": "El valor debe ser mayor a 0"}
                )
        
        # Validar fecha
        if 'due_date' in data and data['due_date'] < timezone.now():
            raise serializers.ValidationError(
                {"due_date": "La fecha no puede ser en el pasado"}
            )
        
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'created_at', 'notification_type', 'is_read']

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'pet', 'activity', 'created_at', 'duration', 'activity_type']