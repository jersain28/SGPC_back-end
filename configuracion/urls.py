# urls.py principal
from django.urls import path, include
from rest_framework_simplejwt import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin
from sgpc.views import MyTokenObtainPairView, detalle_tramite_admin, exportar_tramites_excel, lista_tramites_admin
from sgpc.views import RegisterView, TramiteViewSet, crear_usuario
from rest_framework.routers import DefaultRouter

# Si usas ViewSet, esto es lo más limpio:
router = DefaultRouter()
router.register(r'tramites', TramiteViewSet, basename='tramite')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='auth_register'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/crear-usuario/', crear_usuario, name='crear_usuario'),
    path('api/admin/tramites/', lista_tramites_admin, name='lista_tramites'),
    path('api/admin/tramites/<int:pk>/', detalle_tramite_admin, name='detalle_tramite'),
    path('api/admin/reportes/excel/', exportar_tramites_excel, name='exportar_reporte_excel'),
]