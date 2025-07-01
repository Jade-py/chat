from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from base.forms import CustomLoginForm
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(authentication_form=CustomLoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('chat/', include('base.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # serve static files from this url specified in settings
