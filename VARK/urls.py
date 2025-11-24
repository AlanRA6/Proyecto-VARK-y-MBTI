from django.urls import include, path
from .views import vark_results, vark_test, dashboard_vark, dashboard_data

urlpatterns = [
    path('vark_test/', vark_test, name='vark_test'),
    path('vark_results/', vark_results, name='vark_results'),
    path('vark_dashboard/', dashboard_vark, name='vark_dashboard'),
    path('dashboard-data/', dashboard_data, name='dashboard_data')
]