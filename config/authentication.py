import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
from users.models import User


# Custom Authentication
# https://www.django-rest-framework.org/api-guide/authentication/#example
# ↓ AWS 의 Elastic Beanstalk 등을 이용해서 서버를 deploy 한다면
# WSGIPassAuthorization 를 On 해줘야한다 ↓
# On 설정을 하지않을경우 AWS 는 기본적으로 Authorization 의 header 를 없앤다
# https://www.django-rest-framework.org/api-guide/authentication/#apache-mod_wsgi-specific-configuration
# https://docs.aws.amazon.com/ko_kr/elasticbeanstalk/latest/dg/create-deploy-python-container.html
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
