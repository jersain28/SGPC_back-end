# urls.py principal
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin
from sgpc.views import RegisterView, TramiteViewSet # Asegúrate de importar tu ViewSet o Vista
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
]   