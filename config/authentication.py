import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
from users.models import User


# Custom Authentication
# https://www.django-rest-framework.org/api-guide/authentication/#example


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            # ↓ HEADER 에 포함된 Authentication 정보
            token = request.META.get("HTTP_AUTHENTICATION")
            if token is None:
                return None
            xjwt, jwt_token = token.split(" ")
            decoded = jwt.decode(
                jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
            pk = decoded.get("pk")
            user = User.objects.get(pk=pk)
            return (user, None)  # Documentaion 에 이렇게 하라고나와있음
        except (ValueError, User.DoesNotExist):  # token 이 제대로 보내지지 않을시
            return None
        except jwt.exceptions.DecodeError:  # token 이 제대로 보내지지 않을시
            raise exceptions.AuthenticationFailed(detail="JWT Format Invalid")
        # ↑ same ↓
        # except (ValueError,jwt.exceptions.DecodeError):
        #     return None
