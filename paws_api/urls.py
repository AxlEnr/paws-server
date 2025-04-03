from django.urls import path
from . import views
from .views import LoginView

urlpatterns = [
    # User endpoints
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/login/', LoginView.as_view(), name='login'),
    path('users/signup/', views.signup_user, name='signup_user'),
    
    # Family endpoints
    path('families/', views.family_list, name='family_list'),
    path('families/<int:family_id>/', views.family_detail, name='family_detail'),
    path('families/<int:family_id>/add-member/', views.family_add_member, name='family_add_member'),
    
    # Pet endpoints
    path('pets/', views.pet_list, name='pet_list'),
    path('pets/<int:pet_id>/', views.pet_detail, name='pet_detail'),
    
    # Post endpoints
    path('posts/', views.post_list, name='post_list'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    
    # Reminder endpoints
    path('reminders/', views.reminder_list, name='reminder_list'),
    path('reminders/<int:reminder_id>/', views.reminder_detail, name='reminder_detail'),
    
    # Notification endpoints
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/mark-as-read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    
    # ActivityLog endpoints
    path('activities/', views.activity_log_list, name='activity_log_list'),
    
    # Special endpoints
    path('create-pet-with-post/', views.create_pet_with_post, name='create_pet_with_post'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
]