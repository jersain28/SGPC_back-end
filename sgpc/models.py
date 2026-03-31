from django.db import models
from django.contrib.auth.models import User # Para el Login

def generar_folio():
    ultimo_tramite = Tramite.objects.all().order_by('id').last()
    if not ultimo_tramite:
        return 'SVX-2026-001'
    nuevo_id = ultimo_tramite.id + 1
    return f'SVX-2026-{nuevo_id:03d}'

class Tramite(models.Model):
    ESTADOS_TRAMITE = [
        ('borrador', 'En Registro'), # Cuando el usuario aún no termina de subir todo
        ('revision', 'Esperando Revisión Admin'),
        ('accion_requerida', 'Documentos Rechazados'),
        ('aprobado', 'Finalizado / Permiso Liberado'),
    ]

    # Vinculamos el trámite al ciudadano logueado
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mis_tramites')
    
    folio = models.CharField(max_length=20, unique=True, default=generar_folio, editable=False)
    nombre_fallecido = models.CharField(max_length=200)
    nombre_declarante = models.CharField(max_length=200)
    
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estatus = models.CharField(max_length=20, choices=ESTADOS_TRAMITE, default='borrador')
    
    url_permiso_final = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.folio} - {self.nombre_fallecido}"

class Documento(models.Model):
    ESTADOS_DOC = [
        ('pendiente', 'Pendiente de Revisión'),
        ('aprobado', 'Aprobado ✅'),
        ('rechazado', 'Rechazado ❌'),
    ]

    REQUISITOS = [
        ('INE_Fallecido', 'INE Fallecido'),
        ('Certificado_Defuncion', 'Certificado de Defunción'),
        ('Acta_Defuncion', 'Acta de Defunción'),
        ('Orden_Inhumacion', 'Orden de Inhumación'),
        ('INE_Declarante', 'INE del Declarante'),
        ('Recibo_Pirotecnia', 'Recibo de Pirotecnia'),
        ('Recibo_Semana_Santa', 'Recibo de Semana Santa'),
        ('Recibo_Fiestas_Patrias', 'Recibo de Fiestas Patrias'),
        ('Recibo_Agua', 'Recibo de Agua Potable'),
        ('Recibo_Cooperaciones', 'Recibo de Cooperaciones'),
    ]

    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='documentos')
    tipo_documento = models.CharField(max_length=50, choices=REQUISITOS)
    ruta_supabase = models.URLField(max_length=500) 
    
    # CAMBIO IMPORTANTE: Estado detallado en lugar de Boolean
    estado = models.CharField(max_length=20, choices=ESTADOS_DOC, default='pendiente')
    
    observaciones = models.TextField(null=True, blank=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    revisado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='revisiones_hechas')

    def __str__(self):
        return f"{self.tipo_documento} - {self.estado}"