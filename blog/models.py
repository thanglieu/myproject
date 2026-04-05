from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    GENDER_CHOICES = [
        ('Nam', 'Nam'),
        ('Nữ', 'Nữ'),
    ]
    name = models.CharField()  
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    birth = models.DateField(null=True, blank=True)  
    email = models.EmailField(unique=True)  
    mark = models.IntegerField(default=0)   

    def __str__(self):
        return self.username

class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=255)
    like = models.IntegerField(default=0)
    content = RichTextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ManyToManyField(Topic, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.author} on {self.article}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')

    def __str__(self):
        return f"{self.user} liked {self.article}"



