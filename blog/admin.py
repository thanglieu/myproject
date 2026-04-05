from django.contrib import admin
from .models import Article, Topic, User, Comment, Like

admin.site.register(Article)
admin.site.register(User)
admin.site.register(Topic)
admin.site.register(Comment)
admin.site.register(Like)