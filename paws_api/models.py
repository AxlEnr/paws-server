from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    registration_date = models.DateTimeField(default=timezone.now)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    username = None
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=60)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Family(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='families')
    codeFam = models.CharField(max_length=10, default='No Code')
    creation_date = models.DateTimeField(default=timezone.now)
    
    
    def __str__(self):
        return self.name

class Pet(models.Model):
    PET_TYPES = [
        ('DOG', 'Perro'),
        ('CAT', 'Gato'),
        ('BIRD', 'Ave'),
        ('FISH', 'Pez'),
        ('RODENT', 'Roedor'),
        ('REPTILE', 'Reptil'),
        ('OTHER', 'Otro'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=10, choices=PET_TYPES)
    age = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    breed = models.CharField(max_length=100)
    adoption_date = models.DateField(null=True)
    photo = models.ImageField(upload_to='pets/photos/', null=True, blank=True)  # Cambiado de URLField a ImageField
    vaccines = models.FileField(upload_to='pets/vaccines/', null=True, blank=True) 
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='pets', null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.family and self.owner:
            family = self.owner.families.first()
            if family:
                self.family = family
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.get_pet_type_display()})"
    
    @property
    def photo_url(self):
        if self.photo:
            return self.photo.url
        return None
    
    @property
    def vaccines_url(self):
        if self.vaccines:
            return self.vaccines.url
        return None

class Post(models.Model):
    POST_TYPES = [
        ('REMINDER', 'Recordatorio'),
        ('UPDATE', 'Actualización'),
        ('EVENT', 'Evento'),
        ('OTHER', 'Otro'),
    ]
    
    POST_STATUS = [
        ('ACTIVE', 'Activo'),
        ('ARCHIVED', 'Archivado'),
        ('DELETED', 'Eliminado'),
    ]
    
    pet = models.ForeignKey(Pet, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    post_type = models.CharField(max_length=10, choices=POST_TYPES)
    status = models.CharField(max_length=10, choices=POST_STATUS, default='ACTIVE')
    
    def __str__(self):
        return f"Post by {self.author.email} at {self.created_at}"

class PostImage(models.Model):
    VISIBILITY_CHOICES = [
        ('PERSONAL', 'Personal'),
        ('FAMILY', 'Familia'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    photo = models.ImageField(upload_to='posts/photos/', null=True, blank=True)
    upload_date = models.DateTimeField(default=timezone.now)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='FAMILY')
    caption = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Foto de {self.pet.name} subida por {self.author.first_name}"
    
    def __str__(self):
        return f"Foto de {self.pet.name} subida por {self.author.first_name}"

class Reminder(models.Model):
    REMINDER_TYPES = [
        ('HEALTH', 'Salud'),
        ('ACTIVITY', 'Actividad'),
        ('FOOD', 'Alimentación'),
        ('OTHER', 'Otro'),
    ]
    
    REMINDER_STATUS = [
        ('PENDING', 'Pendiente'),
        ('COMPLETED', 'Completado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateTimeField(default=timezone.now)
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPES)
    status = models.CharField(max_length=10, choices=REMINDER_STATUS, default='PENDING')
    
    def __str__(self):
        return f"{self.title} for {self.pet.name}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('REMINDER', 'Recordatorio'),
        ('MESSAGE', 'Mensaje'),
        ('POST', 'Publicación'),
        ('OTHER', 'Otro'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Notification for {self.user.email}"

class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ('WALK', 'Paseo'),
        ('PLAY', 'Juego'),
        ('TRAINING', 'Entrenamiento'),
        ('FEEDING', 'Alimentación'),
        ('OTHER', 'Otro'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='activities')
    activity = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(blank=True, null=True)
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPES)
    
    def __str__(self):
        return f"{self.get_activity_type_display()} with {self.pet.name}"
