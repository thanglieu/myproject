from django.urls import path
from . import views

app_name = 'exam'

urlpatterns = [
    # tạo trang chọn tittle và số lượng câu hỏi
    path('create/', views.create_test_count, name='create_test_count'),

    # tạo Test
    path('create/<int:question_count>/<str:title>', views.create_test, name='create_test'),

    # làm test
    path('take/<int:test_id>/', views.take_test, name='take_test'),

    # trang chủ
    path('', views.exam_home, name='exam_home'),

    # danh sách Test của User
    path('user/<int:user_id>/', views.user_tests_list, name='user_tests_list'),

    # danh sách người đã làm Test (danh sách UserTest của Test)
    path('test/<int:test_id>/', views.user_test, name='user_test'),

    # chi tiết bài làm (danh sách UserAnswer của UserTest)
    path('test/result/<int:user_test_id>/', views.user_answer, name='user_answer'),
]