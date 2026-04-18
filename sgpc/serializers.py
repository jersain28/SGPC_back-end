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
    # Esto leerá los documentos relacionados y los devolverá como una lista
    documentos = DocumentoSerializer(many=True, read_only=True)
    
    # Mapeos para que React reciba lo que espera (opcional si los nombres ya coinciden)
    # finado = serializers.CharField(source='nombre_finado', read_only=True)

    class Meta:
        model = Tramite
        fields = '__all__'
        read_only_fields = ['folio', 'usuario', 'status']

    def create(self, validated_data):
        # Tu lógica de creación se mantiene aquí si es necesaria
        documentos_data = self.context['request'].data.get('documentos', [])
        tramite = Tramite.objects.create(**validated_data)
        
        for doc in documentos_data:
            Documento.objects.create(tramite=tramite, **doc)
            
        return tramite
