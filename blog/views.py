from django.shortcuts import render, redirect
from .forms import ArticleForm
from .models import Article, Topic
from .models import User
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.core.paginator import Paginator


# trang cá nhân 
def user_page(request):
    user = request.user   # lấy user hiện đang đăng nhập
    return render(request, 'users/user.html', {'user': user})


# đăng ký
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
        #    login(request, user)  # đăng nhập ngay sau khi đăng ký
            return redirect('login')
        else:
            return render(request, 'error.html', {'form': form})
        #    return redirect('error')
        
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


# tìm kiếm
def search(request):
    k = request.GET.get('keyword', '')

    # lọc Article và User theo từ khóa
    list1 = Article.objects.filter(title__icontains=k)
    list2 = User.objects.filter(name__icontains=k)

    # phân trang cho Article
    paginator_articles = Paginator(list1, 10)  
    page_number_articles = request.GET.get('page_articles')
    page_obj_articles = paginator_articles.get_page(page_number_articles)

    # phân trang cho User
    paginator_users = Paginator(list2, 9)  
    page_number_users = request.GET.get('page_users')
    page_obj_users = paginator_users.get_page(page_number_users)

    return render(request, 'search.html', {'articles': page_obj_articles, 'users': page_obj_users,})
            

# danh sách bài viết mới
def article_list(request):
    articles = Article.objects.all().order_by('-created_at')
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', {'posts': page_obj})


# home - danh sách bài viết mới + tìm kiếm
def home(request):
    if not request.GET:
        return article_list(request)
    else:
        return search(request)


# ____________________________________

# lọc
def filter(request):
    topics = Topic.objects.all() 
    selected_topics = request.GET.getlist('topics') 

    articles = Article.objects.filter(topic__id__in=selected_topics).distinct()

    return render(request, 'filter.html', {
        'topics': topics,
        'articles': articles,
        'selected_topics': selected_topics,
    })


"""
def filter(request):
    if request.method == 'GET':
        topic = request.GET.get('tag')

        if not request.GET:
            return render(request, 'filter_form.html')
        else:
            list = Article.objects.filter(tag = topic)
            return render(request, 'article_list.html',{'form' : list})
        
    return render(request, 'error.html')


"""


