from rest_framework import serializers
from .models import Tramite, Documento

class DocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = '__all__'

class TramiteSerializer(serializers.ModelSerializer):
    # Esto permite ver los documentos dentro de la respuesta del trámite
    documentos = DocumentoSerializer(many=True, read_only=True)

    class Meta:
        model = Tramite
        fields = '__all__'