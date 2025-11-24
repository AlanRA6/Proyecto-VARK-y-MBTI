from django.urls import include, path
from .views import mbti_test, mbti_results, dashboard_mbti, dashboard_mbti_data

urlpatterns = [
    path('mbti_test/', mbti_test, name='mbti_test'),
    path('mbti_results/', mbti_results, name='mbti_results'),
    path('mbti_dashboard/', dashboard_mbti, name='mbti_dashboard'),
    path('mbti-dashboard-data/', dashboard_mbti_data, name='dashboard_mbti_data'),
]