from django.urls import path
from . import views

app_name = 'exam'

urlpatterns = [
    # tạo Test 
    path('create/', views.create_test, name='create_test'),

    # làm test
    path('take/<int:test_id>/', views.take_test, name='take_test'),

    # trang chủ
    path('', views.exam_home, name='exam_home'),

    # danh sách người đã làm Test (danh sách UserTest của Test)
    path('test/<int:test_id>/', views.user_test, name='user_test'),

    # chi tiết bài làm (danh sách UserAnswer của UserTest)
    path('test/result/<int:user_test_id>/', views.user_answer, name='user_answer'),

]