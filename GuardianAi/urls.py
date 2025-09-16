from django.contrib import admin
from django.urls import path, include
from main.urls import urlpatterns as main_urls
from api.urls import urlpatterns as api_urls

urlpatterns = [
    path('panel/', admin.site.urls),
    path('', include(main_urls)),
    path('api/', include(api_urls))
]
