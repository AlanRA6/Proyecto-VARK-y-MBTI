from django.urls import include, path
from .views import vark_results, vark_test

urlpatterns = [
    path('vark_test/', vark_test, name='vark_test'),
    path('vark_results/', vark_results, name='vark_results'),
]