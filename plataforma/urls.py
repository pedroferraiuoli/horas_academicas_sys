from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('atividades.urls')),
]

# Handlers de erro personalizados (apenas em produção com DEBUG=False)
handler404 = 'atividades.views.error_handlers.custom_404'
handler500 = 'atividades.views.error_handlers.custom_500'
handler403 = 'atividades.views.error_handlers.custom_403'
handler400 = 'atividades.views.error_handlers.custom_400'
