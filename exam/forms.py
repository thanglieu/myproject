from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Test, Question, Answer


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ["title", "quantity"]


class QuestionCountForm(forms.Form):
    question_count = forms.IntegerField(
        min_value=1,
        max_value=20,
    )
    title = forms.CharField()


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "stt"]
        widgets = {
            "text": CKEditorWidget(),
            "stt": forms.HiddenInput(),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["title", "text", "is_correct"]
        widgets = {
            "title": forms.HiddenInput(),
            "text": CKEditorWidget(),
        }



