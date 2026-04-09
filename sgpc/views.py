from rest_framework import viewsets, permissions
from .models import Tramite
from .serializers import TramiteSerializer
from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer 

class TramiteViewSet(viewsets.ModelViewSet):
    serializer_class = TramiteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # El usuario normal solo ve sus trámites. 
        # El admin (presidente) ve todos.
        if self.request.user.is_staff:
            return Tramite.objects.all()
        return Tramite.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        # Asigna automáticamente el usuario que inició sesión al trámite
        serializer.save(usuario=self.request.user)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "message": "Usuario creado exitosamente",
        })