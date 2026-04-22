from rest_framework import viewsets, permissions
import supabase
from .models import Tramite
from .serializers import TramiteSerializer
from django.contrib.auth.models import User
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import UserSerializer 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from openpyxl import Workbook
from django.http import HttpResponse
from django.utils.timezone import localtime
from django.http import JsonResponse    
from supabase import create_client, Client
from django.conf import settings


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

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Agregamos el campo is_staff al contenido del Token
        token['is_staff'] = user.is_staff
        token['username'] = user.username
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([IsAdminUser]) # <-- Esto bloquea a cualquiera que no sea Admin
def crear_usuario(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Usuario y contraseña son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'El nombre de usuario ya existe'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Creamos el usuario
        user = User.objects.create_user(username=username, password=password)
        
        # CLAVE: Lo hacemos trabajador (is_staff) para que pueda entrar al panel
        user.is_staff = True 
        user.save()

        return Response({'message': 'Trabajador creado exitosamente'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated]) # Solo trabajadores con token pueden ver esto
def lista_tramites_admin(request):
    tramites = Tramite.objects.all().order_by('-creado_el') # Los más nuevos arriba
    serializer = TramiteSerializer(tramites, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def detalle_tramite_admin(request, pk):
    try:
        tramite = Tramite.objects.get(pk=pk)
    except Tramite.DoesNotExist:
        return Response({"error": "No existe"}, status=404)

    # LÓGICA PARA ACTUALIZAR (El botón verde de React usa esto)
    if request.method == 'PATCH':
        # partial=True permite actualizar solo los campos enviados (ej. status_ine_fallecido)
        serializer = TramiteSerializer(tramite, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Devolvemos el trámite actualizado para que React refresque la interfaz
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # LÓGICA PARA LEER (Carga inicial)
    serializer = TramiteSerializer(tramite)
    return Response(serializer.data)
    
def exportar_tramites_excel(request):
    try:
        fecha_inicio_str = request.GET.get('fecha_inicio')
        fecha_fin_str = request.GET.get('fecha_fin')
        status_filtro = request.GET.get('status')

        queryset = Tramite.objects.all()

        # 1. CORRECCIÓN: Cambiar fecha_creacion por creado_el
        if fecha_inicio_str and fecha_fin_str:
            queryset = queryset.filter(
                creado_el__date__gte=fecha_inicio_str,
                creado_el__date__lte=fecha_fin_str
            )
        
        if status_filtro and status_filtro != 'Todos':
            queryset = queryset.filter(status=status_filtro)

        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte"
        ws.append(['Folio', 'Finado', 'Declarante', 'Fecha', 'Estado'])

        for t in queryset:
            # 2. CORRECCIÓN: Cambiar t.fecha_creacion por t.creado_el
            fecha_txt = localtime(t.creado_el).strftime('%d/%m/%Y') if t.creado_el else "S/F"
            
            ws.append([
                getattr(t, 'folio', ''),
                getattr(t, 'nombre_finado', ''),
                getattr(t, 'nombre_declarante', ''),
                fecha_txt,
                getattr(t, 'status', '')
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=reporte.xlsx'
        wb.save(response)
        return response

    except Exception as e:
        print(f"ERROR CRÍTICO EXCEL: {str(e)}")
        return JsonResponse({'details': str(e)}, status=500)
    

@api_view(['PATCH'])
def validar_documento(request, pk):
    try:
        tramite = Tramite.objects.get(pk=pk)
    except Tramite.DoesNotExist:
        return Response({'error': 'Trámite no encontrado'}, status=404)

    # Actualizamos el trámite con los datos que vienen del Admin
    serializer = TramiteSerializer(tramite, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        
        # Lógica extra: Si el admin rechaza algo, el trámite general pasa a 'RECHAZADO'
        # Si aprueba todo, podrías verificar si ya no quedan pendientes
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def generar_permiso(request, pk):
    # Aquí irá la lógica de ReportLab o xhtml2pdf más adelante
    return Response({'message': 'Lógica de PDF en construcción'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_tramites(request):
    # Filtramos por el usuario que tiene la sesión iniciada
    tramites = Tramite.objects.filter(usuario=request.user).order_by('-creado_el')
    serializer = TramiteSerializer(tramites, many=True)
    return Response(serializer.data)

# Agrega esta línea antes de la función corregir_documento
supabase_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def corregir_documento(request, tramite_id):
    try:
        # Buscamos el trámite
        tramite = Tramite.objects.get(id=tramite_id, usuario=request.user)
        
        if not request.FILES:
            return Response({"error": "No se enviaron archivos"}, status=status.HTTP_400_BAD_REQUEST)

        for campo_archivo in request.FILES:
            nuevo_archivo = request.FILES[campo_archivo]
            
            # Extraer extensión y preparar ruta
            file_ext = nuevo_archivo.name.split('.')[-1]
            file_path = f"correcciones/{tramite.folio}_{campo_archivo}.{file_ext}"
            
            # --- CORRECCIÓN AQUÍ: Usamos supabase_client, no supabase ---
            file_content = nuevo_archivo.read()
            supabase_client.storage.from_('requisitos-panteon').upload(
                path=file_path,
                file=file_content,
                file_options={
                    "upsert": "true", 
                    "content-type": nuevo_archivo.content_type
                }
            )

            # Obtener URL pública usando la instancia correcta
            url_publica = supabase_client.storage.from_('requisitos-panteon').get_public_url(file_path)
            
            # Actualización dinámica de los campos del modelo
            setattr(tramite, campo_archivo, url_publica)
            setattr(tramite, f"status_{campo_archivo}", "PENDIENTE")
            setattr(tramite, f"obs_{campo_archivo}", "") 

        # Cambiamos el estado general y guardamos
        tramite.status = "PENDIENTE"
        tramite.save()

        return Response({"message": "Documentos actualizados correctamente"}, status=status.HTTP_200_OK)

    except Tramite.DoesNotExist:
        return Response({"error": "Trámite no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Esto te ayudará a ver el error real en la consola si algo más falla
        print(f"Error detallado: {str(e)}")
        return Response({"error": f"Error en el servidor: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)