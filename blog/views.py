from django.shortcuts import render, redirect, get_object_or_404
from .forms import ArticleForm
from .models import Article, Topic, Comment, Like, Series, Article_List
from .models import User
from .forms import CustomUserCreationForm, ArticleCreateForm, CommentForm, SeriesCreateForm
from django.contrib.auth import login, logout
from django.core.paginator import Paginator
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages


# trang cá nhân 
def user_page(request):
    # hiển thị thông tin cá nhân, danh sách article và các series
    if request.method == 'GET':
        user = request.user
        form = SeriesCreateForm()
        series = Series.objects.filter(author=user)

        k = []
        for i in series:
            a = Article_List.objects.filter(series=i)
            k.append([i,a[0].article if len(a)>0 else None])

        return render(request, 'users/user.html', {
            'user': user,
            'form': form,
            'k': k,
        })
    
    # trường user lấy người dùng hiện tại, chứ không nhập liệu qua <input>
    # do đó không nhập tự động bằng ModelForm được, phải nhập thủ công bằng Form
    elif request.method == 'POST':
        form = SeriesCreateForm(request.POST) 
        if form.is_valid():
            a = request.user
            b = form.cleaned_data['name']
            Series.objects.create(author = a, name = b)
        
        return redirect('series')


# chi tiết user
def user_detail(request, pk):
    # hiển thị thông tin cá nhân, danh sách article và các series
    if request.method == 'GET':
        user = User.objects.get(id=pk)
        form = SeriesCreateForm()
        series = Series.objects.filter(author=user)

        k = []
        for i in series:
            a = Article_List.objects.filter(series=i)
            k.append([i,a[0].article if len(a)>0 else None])

        return render(request, 'users/user.html', {
            'user': user,
            'form': form,
            'k': k,
        })


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
    if(request.GET.get('form')==None): 
        return article_list(request)
    else:
    # nếu HTTP GET có dữ liệu (tức submit form có method = get)
        if(request.GET.get('form')=='search'):    
            return search(request)
        elif(request.GET.get('form')=='logout'):  
            # đăng xuất 
            logout(request)
            return redirect('login')
        else:
            return redirect('error')

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
    # do trường user lấy người dùng hiện tại, chứ không nhập liệu qua <input>
    # do đó không nhập tự động bằng ModelForm được, phải nhập thủ công bằng Form
    elif request.method == 'POST':
        form = ArticleCreateForm(request.POST) 
        if form.is_valid():
            a = request.user
            b = form.cleaned_data['title']
            c = form.cleaned_data['content']
            d = form.cleaned_data['topic']
            article = Article.objects.create(author = a, title = b, content = c)
            
            # do topic là giá trị list [] nên phải dùng set() thay vì create()
            article.topic.set(d)
            form = ArticleCreateForm()
            return redirect('home')
        else:
            print(a,b,c,d)


# ____________ ARTICLE DETAIL, COMMENT, LIKE FUNCTIONALITY ____________

# View chi tiết bài viết kèm comments
def article_detail(request, article_id):

    # hiển thị thông tin bài viết, content
    # hiển thị các bài viết cùng series (nếu có series)
    if request.method == 'GET':
        article = get_object_or_404(Article, id=article_id)
        comments = Comment.objects.filter(article=article).order_by('-created_at')
        user_liked_article = False
        
        if request.user.is_authenticated:
            user_liked_article = Like.objects.filter(user=request.user, article=article).exists()
        
        
        k = Article_List.objects.filter(article=article)
        this_series = k[0].series if len(k)>0 else None


        article_list = Article_List.objects.filter(series=this_series).order_by('id')
        articles_series = [i.article for i in article_list]

        context = {
            'article': article,
            'comments': comments,
            'user_liked_article': user_liked_article,
            'comment_form': CommentForm(),
            'series': Series.objects.filter(author=request.user),
            'articles': articles_series,
            'this_series': this_series,
        }
        
        return render(request, 'articles/article.html', context)
    
    # thêm - xóa series cho article (nếu chưa có)
    elif request.method == 'POST':
        # thêm vào series 
        if(request.POST.get('form')=='add'): 
            # article = Article.objects.get(id=article_id)
            a = get_object_or_404(Article, id=article_id)
            b = Series.objects.get(name=request.POST['series'])

            # tạo Article_List cho Series nếu chưa có
            k = Article_List.objects.create(series=b, article=a)

            # return article_detail(request, article_id), gọi lại hàm nhưng không kích hoạt GET request
            return redirect('article', article_id=a.id)
            
        # xóa series
        elif (request.POST.get('form')=='delete'): 
            a = get_object_or_404(Article, id=article_id)
            b = Article_List.objects.filter(article=a).first().series
            Article_List.objects.get(series=b, article=a).delete()
            return redirect('article', article_id=a.id)



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


#-------------------------------------
# chỉnh sửa bài viết
def edit_article(request, pk):
    article = get_object_or_404(Article, id=pk)

    if request.method == 'GET':
        # khởi tạo form với dữ liệu sẵn có
        form = ArticleCreateForm(initial={
            'title': article.title,
            'content': article.content,
            'topic': article.topic.all(),
        })
        return render(request, 'articles/create.html', {'form': form, 'article': article})

    elif request.method == 'POST':
        form = ArticleCreateForm(request.POST)
        if form.is_valid():
            article.author = request.user
            article.title = form.cleaned_data['title']
            article.content = form.cleaned_data['content']
            article.topic.set(form.cleaned_data['topic'])
            article.save()
            return redirect('article', article_id=article.id)
        else:
            return render(request, 'articles/create.html', {'form': form})


# xóa bài viết
def delete_article(request, pk):
    if request.method == 'GET':
        return render(request, 'confirm.html')
    elif request.method == 'POST':
        article = get_object_or_404(Article, id=pk)
        article.delete()
        return redirect('home')









