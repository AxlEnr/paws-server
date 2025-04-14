from django.utils import timezone
from datetime import timedelta
from django_q.tasks import schedule
from models import Reminder

def check_recurring_reminders():
    now = timezone.now()
    twelve_hours_ago = now - timedelta(hours=12)
    
    reminders = Reminder.objects.filter(
        status='COMPLETED',
        is_recurring=True,
        next_due_date__lte=now,
        last_completed__lte=twelve_hours_ago
    )
    
    for reminder in reminders:
        reminder.status = 'PENDING'
        reminder.save()
        
        # Programar notificación
        schedule(
            'paws.tasks.send_reminder_notification',
            reminder.id,
            schedule_type='O',
            next_run=reminder.next_due_date
        )