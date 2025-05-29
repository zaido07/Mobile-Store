# middleware.py
from django.utils import timezone
from .models import ActivityLog
import json

class ActivityLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            if not request.path.startswith('/admin/'):
                try:
                    data = {
                        'path': request.path,
                        'method': request.method,
                        'data': dict(request.POST) if request.method == 'POST' else None,
                    }
                    
                    ActivityLog.objects.create(
                        user=request.user,
                        action='OTHER',
                        model_name='Request',
                        details=data,
                        ip_address=self.get_client_ip(request)
                    )
                except Exception as e:
                    # Log to console if saving fails
                    print(f"Failed to save activity log: {e}")
        
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip