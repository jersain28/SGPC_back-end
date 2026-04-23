from django.db import models
from django.contrib.auth.models import User
import uuid
import datetime


class Tramite(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'En Revisión'),
        ('RECHAZADO', 'Acción Requerida'),
        ('APROBADO', 'Aprobado'),
        ('FINALIZADO', 'Permiso Generado'),
    ]

    # Opciones para la validación individual de cada archivo
    ESTADO_DOC = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]

    # Información básica
    folio = models.CharField(max_length=20, unique=True, editable=False) 
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tramites')
    nombre_finado = models.CharField(max_length=255)
    # Corrección para evitar errores de integridad
    fecha_nacimiento = models.DateField(null=True, blank=True) 
    nombre_declarante = models.CharField(max_length=255)
    parentesco = models.CharField(max_length=100)
    email_declarante = models.EmailField(max_length=255, blank=True, null=True)
    telefono_declarante = models.CharField(max_length=20, blank=True, null=True)

    
    # --- DOCUMENTOS Y VALIDACIÓN INDIVIDUAL ---
    
    # 1. INE del Fallecido
    ine_fallecido = models.URLField(max_length=500, blank=True, null=True)
    status_ine_fallecido = models.CharField(max_length=20, choices=ESTADO_DOC, default='PENDIENTE')
    obs_ine_fallecido = models.TextField(blank=True, null=True)

    # 2. INE del Declarante
    ine_declarante = models.URLField(max_length=500, blank=True, null=True)
    status_ine_declarante = models.CharField(max_length=20, choices=ESTADO_DOC, default='PENDIENTE')
    obs_ine_declarante = models.TextField(blank=True, null=True)

    # 3. Certificado de Defunción
    cert_defuncion = models.URLField(max_length=500, blank=True, null=True)
    status_cert_defuncion = models.CharField(max_length=20, choices=ESTADO_DOC, default='PENDIENTE')
    obs_cert_defuncion = models.TextField(blank=True, null=True)

    # 4. Acta de Defunción
    acta_defuncion = models.URLField(max_length=500, blank=True, null=True)
    status_acta_defuncion = models.CharField(max_length=20, choices=ESTADO_DOC, default='PENDIENTE')
    obs_acta_defuncion = models.TextField(blank=True, null=True)

    # 5. Orden de Inhumación
    orden_inhumacion = models.URLField(max_length=500, blank=True, null=True)
    status_orden_inhumacion = models.CharField(max_length=20, choices=ESTADO_DOC, default='PENDIENTE')
    obs_orden_inhumacion = models.TextField(blank=True, null=True)

    # 6. Recibo Semana Santa
    recibo_semana_santa = models.URLField(max_length=500, blank=True, null=True)
    status_recibo_ss = models.CharField(max_length=20, choices=ESTADO_DOC, default='PENDIENTE')
    obs_recibo_ss = models.TextField(blank=True, null=True)

    # 7. Recibo Agua Potable
    recibo_agua = models.URLField(max_length=500, blank=True, null=True)
    status_recibo_agua = models.CharField(max_length=20, choices=ESTADO_DOC, default='PENDIENTE')
    obs_recibo_agua = models.TextField(blank=True, null=True)

    # 8. Recibo Pirotecnia
    recibo_pirotecnia = models.URLField(max_length=500, blank=True, null=True)
    status_recibo_piro = models.CharField(max_length=20, choices=ESTADO_DOC, default='PENDIENTE')
    obs_recibo_piro = models.TextField(blank=True, null=True)

    # 9. Fiestas Patronales
    recibo_patronales = models.URLField(max_length=500, blank=True, null=True)
    status_recibo_patronales = models.CharField(max_length=20, choices=ESTADO_DOC, default='PENDIENTE')
    obs_recibo_patronales = models.TextField(blank=True, null=True)

    # 10. Recibo Coop. Extras (Opcional)
    recibo_extras = models.URLField(max_length=500, blank=True, null=True)
    status_recibo_extras = models.CharField(max_length=20, choices=ESTADO_DOC, default='PENDIENTE')
    obs_recibo_extras = models.TextField(blank=True, null=True)

    
    # 3. Campos de control y resultados
    pdf_permiso = models.URLField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.folio} - {self.nombre_finado}"

    def save(self, *args, **kwargs):
        if not self.folio:
            hoy = datetime.date.today()
            anio = hoy.year
            # Filtramos por el año de la fecha actual para generar el folio
            ultimo = Tramite.objects.filter(creado_el__year=anio).last()
            if ultimo:
                try:
                    # Extraemos el número después del último guion
                    num = int(ultimo.folio.split('-')[-1]) + 1
                    self.folio = f"SVX-{anio}-{num:03d}"
                except (ValueError, IndexError):
                    self.folio = f"SVX-{anio}-001"
            else:
                self.folio = f"SVX-{anio}-001"
        super().save(*args, **kwargs)

class Documento(models.Model):
    ESTADOS_DOC = [('PENDIENTE', 'Pendiente'), ('APROBADO', 'Aprobado'), ('RECHAZADO', 'Rechazado')]
    
    tramite = models.ForeignKey(Tramite, related_name='documentos', on_delete=models.CASCADE)
    tipo_documento = models.CharField(max_length=100) # Ej: "INE Fallecido"
    archivo_url = models.URLField() # URL de Supabase Storage
    estado = models.CharField(max_length=20, choices=ESTADOS_DOC, default='PENDIENTE')
    motivo_rechazo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo_documento} - {self.tramite.folio}"