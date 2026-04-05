from django.shortcuts import render, redirect, get_object_or_404
from .forms import ArticleForm
from .models import Article, Topic, Comment, Like
from .models import User
from .forms import CustomUserCreationForm, ArticleCreateForm, CommentForm
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.db.models import Count


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
    k = request.GET.get('keyword', '').strip()

    # Chỉ tìm kiếm nếu keyword không rỗng
    if k:
        list1 = Article.objects.filter(title__icontains=k)
        list2 = User.objects.filter(name__icontains=k)
    else:
        list1 = Article.objects.none()
        list2 = User.objects.none()

    # phân trang cho Article
    paginator_articles = Paginator(list1, 10)  
    page_number_articles = request.GET.get('page_articles')
    page_obj_articles = paginator_articles.get_page(page_number_articles)

    # phân trang cho User
    paginator_users = Paginator(list2, 9)  
    page_number_users = request.GET.get('page_users')
    page_obj_users = paginator_users.get_page(page_number_users)

    return render(request, 'search.html', {
        'articles': page_obj_articles, 
        'users': page_obj_users,
        'keyword': k
    })
            

# danh sách bài viết mới
def article_list(request):
    articles = Article.objects.all().order_by('-created_at')
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', {'posts': page_obj})


# home - danh sách bài viết mới + tìm kiếm
def home(request):
    # nếu HTTP GET rỗng không có dữ liệu (tức kích hoạt bởi gõ URL)
    if not request.GET:
        return article_list(request)
    else:
    # nếu HTTP GET có dữ liệu (tức submit form có method = get)
        print(request.GET)
        if(request.GET.get('form')=='search'):    
            return search(request)
        elif(request.GET.get('form')=='logout'):  
            # đăng xuất 
            logout(request)
            return redirect('login')
        elif(request.GET.get('form')=='create'): 
            return redirect('create')
        elif(request.GET.get('form')=='filter'): 
            return redirect('filter')
        elif(request.GET.get('form')=='user'): 
            return redirect('this_user')
        elif(request.GET.get('form')=='BXH'): 
            return redirect('user-list')

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

# tạo bài viết
def create_article(request):
    if request.method == 'GET':
        form = ArticleCreateForm()
        return render(request, 'articles/create.html', {'form': form})
    
    # xử lý thao tác submit bài viết
    # do trường user lấy người dùng hiện tại qua HTTP request chứ không nhập input qua form
    # do đó ta dùng forms.Form để nhập liệu thủ công thay vì dùng forms.ModelForm
    elif request.method == 'POST':
        form = ArticleCreateForm(request.POST) 
        if form.is_valid():
            a = request.user
            b = form.cleaned_data['title']
            c = form.cleaned_data['content']
            d = form.cleaned_data['topic']
            article = Article.objects.create(author = a, title = b, content = c)
            article.topic.set(d)
            form = ArticleCreateForm()
            return redirect('home')
        else:
            print(a,b,c,d)


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


# ____________ ARTICLE DETAIL, COMMENT, LIKE FUNCTIONALITY ____________

# View chi tiết bài viết kèm comments
def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    comments = Comment.objects.filter(article=article).order_by('-created_at')
    user_liked_article = False
    
    if request.user.is_authenticated:
        user_liked_article = Like.objects.filter(user=request.user, article=article).exists()
    
    context = {
        'article': article,
        'comments': comments,
        'user_liked_article': user_liked_article,
        'comment_form': CommentForm(),
    }
    
    return render(request, 'articles/article.html', context)


# Tạo comment cho bài viết
@login_required(login_url='login')
def create_comment(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.article = article
            comment.save()
            return redirect('article', article_id=article_id)
    
    return redirect('article', article_id=article_id)


# Like bài viết
@login_required(login_url='login')
def like_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    user = request.user
    
    # Kiểm tra xem user đã like chưa
    like = Like.objects.filter(user=user, article=article).first()
    
    if like:
        # Nếu đã like, xóa like đi
        like.delete()
    else:
        # Nếu chưa like, tạo like và tăng mark của article author
        Like.objects.create(user=user, article=article)
        article.author.mark += 1
        article.author.save()
    
    return redirect('article', article_id=article_id)


