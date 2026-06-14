from django.db import models
from blog.models import User, Topic

class Practice(models.Model):
    title = models.CharField()
    content = models.TextField()
    code = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ManyToManyField(Topic, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)   


class TestCase(models.Model):
    stt = models.IntegerField()
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE)
    input = models.TextField()
    output = models.TextField()


class UserPractice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE)
    mark = models.IntegerField(default=0)
    user_code = models.TextField()
    language = models.TextField(default='')








