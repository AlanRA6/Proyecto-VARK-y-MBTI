from django.urls import include, path
from django.contrib.auth import views as auth_views
from .views import contact, home, services, validate_token

urlpatterns = [
    path('', home, name='home'),
    path('services/', services, name='services'),
    path('contact/', contact, name='contact'),
    # URL DE LOGIN
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('validate_token/<str:token>/', validate_token, name='validate_token'),
]