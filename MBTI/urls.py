from django.urls import include, path
from .views import mbti_test, mbti_results

urlpatterns = [
    path('mbti_test/', mbti_test, name='mbti_test'),
    path('mbti_results/', mbti_results, name='mbti_results'),
]