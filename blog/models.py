from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser

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

class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)

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
    like = models.IntegerField(default=0)
    content = models.TextField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


