# sgpc/admin.py
from django.contrib import admin
from .models import Tramite, Documento # Importamos tus modelos

class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 0
    readonly_fields = ('tipo_documento', 'archivo_url')

@admin.register(Tramite)
class TramiteAdmin(admin.ModelAdmin):
    # Campos que verás en la lista principal
    list_display = ('folio', 'nombre_finado', 'status', 'creado_el')
    # Permite buscar por nombre o folio
    search_fields = ('folio', 'nombre_finado')
    # Agrega los documentos dentro de la vista del trámite
    inlines = [DocumentoInline]

# También registramos Documento por separado por si quieres ver la lista global
@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('tipo_documento', 'tramite', 'estado')
    list_filter = ('estado', 'tipo_documento')