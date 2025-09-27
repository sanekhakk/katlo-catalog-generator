from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('katloapp.urls')),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('logout/', LogoutView.as_view(next_page='/'), name='business_logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)