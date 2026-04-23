from django import views
from django.urls import path, include
from django.contrib import admin
from sgpc.views import MyTokenObtainPairView,  corregir_documento, detalle_tramite_admin, exportar_tramites_excel, finalizar_y_generar_pdf, lista_tramites_admin
from sgpc.views import RegisterView, TramiteViewSet, crear_usuario
from rest_framework.routers import DefaultRouter
# 1. IMPORTACIÓN CORRECTA DE JWT (Añade .views)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# 2. IMPORTACIÓN DE TUS VISTAS (Usa un alias para evitar confusiones)
from sgpc import views as sgpc_views


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
    path('admin/tramites/<int:pk>/validar/', sgpc_views.validar_documento, name='validar_documento'),
    path('api/mis-tramites/', sgpc_views.mis_tramites, name='mis_tramites'),
    path('api/tramites/<int:tramite_id>/corregir/', sgpc_views.corregir_documento, name='corregir_documento'),
    path('api/tramites/<int:id>/finalizar/', finalizar_y_generar_pdf, name='finalizar-tramite'),
]