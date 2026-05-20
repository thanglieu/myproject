from django.urls import path
from . import views

app_name = 'practice'

urlpatterns = [
    path('run-code/', views.run_practice, name='run_code'),
    path('create/', views.create_practice, name='create'),
    path('', views.practice_list, name='practice_list'),
    path('<int:practice_id>/', views.user_practice_list, name='user_practice_list'),
    path('<int:practice_id>/take/', views.take_practice, name='take_practice'),
    path('user_practice/<int:practice_id>/<int:user_id>/', views.user_practice, name='user_practice'),
]
