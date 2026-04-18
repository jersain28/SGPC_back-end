from rest_framework import viewsets, permissions
from .models import Tramite
from .serializers import TramiteSerializer
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_tramite_admin(request, pk):
    try:
        tramite = Tramite.objects.get(pk=pk)
        serializer = TramiteSerializer(tramite)
        return Response(serializer.data)
    except Tramite.DoesNotExist:
        return Response({"error": "No existe"}, status=404)
    
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