from django.urls import path
from . import views

app_name = 'exam'

urlpatterns = [
    path('create/', views.create_test_count, name='create_test_count'),
    path('create/<int:question_count>/', views.create_test, name='create_test'),
    path('', views.search_tests, name='search_tests'),
    path('mine/', views.my_tests, name='my_tests'),
    path('user/<int:user_id>/', views.user_tests, name='user_tests'),
    path('take/<int:test_id>/', views.take_test, name='take_test'),
    path('result/<int:user_test_id>/', views.test_result, name='test_result'),
]