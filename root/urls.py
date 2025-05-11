from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.users.urls')),
    path('exercises/', include('apps.exercises.urls')),
    path('chats/', include('apps.chats.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document=settings.MEDIA_ROOT)
