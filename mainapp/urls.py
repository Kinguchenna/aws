
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from userauths.views import register,login_view,logout_view, check_mail,reset_password

urlpatterns = [
    path('', views.home, name='home'),
    path("register", register, name="register"),
     path("login", login_view, name="login_view"),
     path("logout", logout_view, name="logout_view"),
     path("location-list", views.gelLocationList, name="location-list"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)