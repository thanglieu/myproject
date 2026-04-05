from django.urls import path
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, CreateView, TemplateView, DetailView
from . import views
from .models import Article, User

urlpatterns = [

    # đăng nhập
    path('login/', 
        LoginView.as_view(
            template_name='login.html',
            # đặt URL chuyển hướng đến sau khi đăng nhập
            redirect_authenticated_user=True,
            next_page = '/'
        ), 
        name='login'
    ),

    # đăng ký
    path('register/', views.register, name='register'),

    # trang cá nhân
    path('users/this-user', views.user_page, name='this_user'),

    # tạo bài viết mới
    path('articles/new/', views.create_article, name = 'create'),


    # danh sách User sắp xếp theo mark
    path('users/rank/',        
        ListView.as_view( 
            model=User, 
            template_name='users/users_list.html', 
            context_object_name='users',
            queryset=User.objects.order_by("-mark")
        ), 
        name='user-list'
    ),


    # trang chủ
    path('',views.home, name = 'home'),


    # tìm kiếm
    path('search/', views.search, name="search"),


    # lọc
    path('filter/', views.filter, name="filter"),

    # chi tiết bài viết
    path('articles/<int:article_id>/', views.article_detail, name='article'),
    
    # comments
    path('articles/<int:article_id>/comment/', views.create_comment, name='create_comment'),
    
    # likes
    path('articles/<int:article_id>/like/', views.like_article, name='like_article'),

    # chi tiết người dùng
    path('users/<int:pk>/',        
        DetailView.as_view( 
            model=User, 
            template_name='users/user.html', 
            context_object_name='user',
        ), 
        name='user'
    ),

    path('error/',        
        TemplateView.as_view( 
            template_name='error.html', 
        ), 
        name='error'
    ),
]

"""
# tạo bài viết mới
path('articles/new/', 
    CreateView.as_view( 
        model=Article, 
        template_name='articles/create.html', 
        fields=['title', 'content', 'topic','author'], 
        success_url = reverse_lazy('home'),

    ),
    name = 'create'
),
"""
