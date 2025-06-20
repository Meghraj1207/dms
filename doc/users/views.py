from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.serializers import ModelSerializer
from django.utils import timezone
from datetime import datetime, timezone as dt_timezone

from .models import User, UserSessionLog
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer


# Custom permission: Only admin can access view
class IsAdminUserCustom(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


# Serializer for registering users
class RegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('u_name', 'password', 'email', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            u_name=validated_data['u_name'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            role=validated_data.get('role', 'initiator')  # Default role
        )
        return user


# View for registering users (only admin)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    serializer_class = RegisterSerializer


# Login view returning tokens + user info
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


# Custom token serializer — logs login time & expiry
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


# Custom token view — using our token serializer
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# Logout view — logs logout time in latest session
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    latest_session = UserSessionLog.objects.filter(user=request.user).order_by('-login_time').first()

    if latest_session and not latest_session.logout_time:
        latest_session.logout_time = timezone.now()
        latest_session.save()

    return Response({'message': 'Logout recorded'}, status=200)
