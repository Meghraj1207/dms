from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken
from .models import UserSessionLog
from django.utils import timezone
from datetime import timezone as dt_timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from datetime import datetime

class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('u_name', 'password', 'email','role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            u_name=validated_data['u_name'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            role=validated_data.get('role', 'initiator')
        )
        return user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        access_token = self.get_token(self.user)

        expiry_time = access_token['exp']
        expiry_dt = datetime.fromtimestamp(expiry_time, tz=dt_timezone.utc)

        UserSessionLog.objects.create(
            user=self.user,
            login_time=timezone.now(),
            token_expiry=expiry_dt
        )

        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    # Get the latest session for the current user
    latest_session = UserSessionLog.objects.filter(user=request.user).order_by('-login_time').first()
    
    if latest_session and not latest_session.logout_time:
        latest_session.logout_time = timezone.now()
        latest_session.save()
    
    return Response({'message': 'Logout recorded'}, status=200)