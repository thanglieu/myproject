from django.contrib import admin
from .models import Test, Answer, UserAnswer, UserTest, Question

admin.site.register(Test)
admin.site.register(Answer)
admin.site.register(UserAnswer)
admin.site.register(UserTest)
admin.site.register(Question)
