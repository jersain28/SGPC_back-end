from rest_framework import serializers
from .models import Tramite, Documento 
from django.contrib.auth.models import User

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
    documentos = DocumentoSerializer(many=True, required=False)

    class Meta:
        model = Tramite
        fields = '__all__'
        read_only_fields = ['folio', 'usuario', 'status'] #

    def create(self, validated_data):
        documentos_data = validated_data.pop('documentos', [])
        
        # El usuario se recupera del perform_create del viewset
        tramite = Tramite.objects.create(**validated_data)
        
        for doc in documentos_data:
            # Solo creamos el registro si tiene una URL válida
            if doc.get('archivo_url'):
                Documento.objects.create(tramite=tramite, **doc) #
            
        return tramite