from rest_framework import serializers
from .models import Tramite, Documento 
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento #
        fields = ['tipo_documento', 'archivo_url']

class TramiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tramite
        fields = '__all__'
        # Mantenemos estos como solo lectura para que el usuario no los altere manualmente
        read_only_fields = ['folio', 'usuario', 'creado_el', 'actualizado_el']

    def create(self, validated_data):
        # Asignamos automáticamente el usuario que hace la petición
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['usuario'] = request.user
        return super().create(validated_data)
