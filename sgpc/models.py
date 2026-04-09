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

    # Información del finado y declarante
    folio = models.CharField(max_length=20, unique=True, editable=False) 
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tramites')
    nombre_finado = models.CharField(max_length=255)
    fecha_nacimiento = models.DateField()
    nombre_declarante = models.CharField(max_length=255)
    parentesco = models.CharField(max_length=100)
    email_declarante = models.EmailField(max_length=255, blank=True, null=True)
    telefono_declarante = models.CharField(max_length=20, blank=True, null=True)
    
    # Estado general del trámite
    status = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.folio:
            anio = datetime.date.today().year
            ultimo = Tramite.objects.filter(creado_el__year=anio).last()
            if ultimo:
                # Lógica para sumar 1
                num = int(ultimo.folio.split('-')[-1]) + 1
                self.folio = f"SVX-{anio}-{num:03d}"
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