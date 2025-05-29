# authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            # Get the token from the request
            header = self.get_header(request)
            if header is None:
                return None

            raw_token = self.get_raw_token(header)
            validated_token = self.get_validated_token(raw_token)
            
            # Check if token is blacklisted
            jti = validated_token['jti']
            if cache.get(f'access_blacklist_{jti}'):
                raise InvalidToken('Token has been blacklisted')

            return self.get_user(validated_token), validated_token
        except Exception as e:
            raise InvalidToken(str(e))
        
# authentication.py


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token['user_id']
            user = self.user_model.objects.get(pk=user_id)
            
            # Verify token claims match user status
            if validated_token.get('is_staff') != user.is_staff:
                raise AuthenticationFailed('Token admin status mismatch')
                
            return user
        except Exception as e:
            raise AuthenticationFailed(str(e))