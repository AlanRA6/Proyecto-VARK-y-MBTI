from django.urls import include, path
from .views import post_token, teachers_home, tokens_view, revoke_token, get_reports, vark_individual_report, mbti_individual_report, buscar_token

urlpatterns = [
    path('', teachers_home, name='teachers_home'),
    path('tokens/', tokens_view, name='tokens_view'),
    path('post_token/', post_token, name='post_token'),
    path('revoke_token/', revoke_token, name='revoke_token'),
    path('reports/', get_reports, name='reports_list'),
    path('vark_report/<int:id>/', vark_individual_report, name='vark_individual_report'),
    path('mbti_report/<int:id>/', mbti_individual_report, name='mbti_individual_report'),
    path('search_token/<str:token>/<str:type>/', buscar_token, name='search_token'),
]