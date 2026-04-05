from django import forms
from django.contrib.auth import get_user_model
from .models import Topic, Article, Comment, User
from django.contrib.auth.forms import UserCreationForm
from ckeditor.widgets import CKEditorWidget


User = get_user_model()

class CustomUserCreationForm(UserCreationForm): 
    class Meta(UserCreationForm.Meta): 
        model = User 
        fields = ('username', 'name', 'gender', 'birth', 'email')


# Form cho User (Custom User Model)
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'name', 'gender', 'birth', 'email', 'mark', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name']


class ArticleForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Article
        fields = ['title', 'content', 'topic']


class ArticleCreateForm(forms.Form):
    title = forms.CharField(max_length=255)
    content = forms.CharField(widget=CKEditorWidget())
    topic = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=forms.SelectMultiple,   # hoặc CheckboxSelectMultiple
        required=False
    )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Viết bình luận...'})
        }
