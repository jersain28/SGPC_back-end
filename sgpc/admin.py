# sgpc/admin.py

from django.contrib import admin
from .models import Documento, Tramite

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    # Antes tenías 'validado' en la posición 2, cámbialo por 'estado'
    list_display = ('tipo_documento', 'tramite', 'estado') 
    
    # También cámbialo en el filtro lateral
    list_filter = ('estado', 'tipo_documento') 
    
    search_fields = ('tramite__folio', 'tipo_documento')