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
        label="Số lượng câu hỏi",
        help_text="Nhập số lượng câu hỏi bạn muốn tạo cho bài kiểm tra."
    )


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "stt"]
        widgets = {
            "text": CKEditorWidget(),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ["title", "text", "is_correct"]
        widgets = {
            "text": CKEditorWidget(),
        }



