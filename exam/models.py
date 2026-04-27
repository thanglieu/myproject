from django.db import models
from blog.models import User
from ckeditor.fields import RichTextField

class Test(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    '''
    chỉ cho làm Test trong thời gian quy định
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    '''


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text = RichTextField()
    stt = models.PositiveIntegerField(default=0)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    title = models.CharField(default='a')
    text = RichTextField()
    is_correct = models.BooleanField(default=False)


# Bảng trung gian: User làm Test
class UserTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_tests")
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="user_tests")
    score = models.FloatField(blank=True, null=True)


# Bảng trung gian: User chọn Answer cho Question
class UserAnswer(models.Model):
    test = models.ForeignKey(UserTest, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    '''
    nếu muốn sắp xếp theo thứ tự nộp
    submitted_at = models.DateTimeField(auto_now_add=True)
    '''

    class Meta:
        unique_together = ("test", "answer")  # mỗi câu hỏi chỉ có 1 lựa chọn

