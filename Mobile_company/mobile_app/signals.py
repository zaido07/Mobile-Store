# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from .models import ActivityLog

User = get_user_model()

@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if sender.__name__ == 'ActivityLog' or sender.__name__ == 'LogEntry':
        return
    
    user = None
    if hasattr(instance, 'request') and hasattr(instance.request, 'user'):
        user = instance.request.user
    elif hasattr(instance, 'user'):
        user = instance.user
    
    action = 'CREATE' if created else 'UPDATE'
    
    try:
        changes = {}
        if not created and hasattr(instance, 'get_changes'):
            changes = instance.get_changes()
        
        ActivityLog.objects.create(
            user=user,
            action=action,
            model_name=sender.__name__,
            instance_id=str(instance.pk),
            details={
                'fields': changes if changes else 'All fields',
                'new_values': {field.name: str(getattr(instance, field.name)) 
                              for field in instance._meta.fields
                              if field.name != 'password'}
            }
        )
    except Exception as e:
        print(f"Failed to log save: {e}")

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender.__name__ == 'ActivityLog' or sender.__name__ == 'LogEntry':
        return
    
    user = None
    if hasattr(instance, 'request') and hasattr(instance.request, 'user'):
        user = instance.request.user
    
    try:
        ActivityLog.objects.create(
            user=user,
            action='DELETE',
            model_name=sender.__name__,
            instance_id=str(instance.pk),
            details={
                'deleted_object': str(instance)
            }
        )
    except Exception as e:
        print(f"Failed to log delete: {e}")