from django import forms
from .models import TestCase

class PracticeForm(forms.Form):
    title = forms.CharField(max_length=255)
    content = forms.CharField(widget=forms.Textarea)
    code = forms.CharField(widget=forms.Textarea)


class TestCaseForm(forms.ModelForm):
    class Meta:
        model = TestCase
        fields = ['input','output']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # output không bắt buộc nhập
        self.fields['output'].required = False


class UserPracticeForm(forms.Form):
    user = forms.IntegerField()  # hoặc ModelChoiceField
    practice = forms.IntegerField()
    mark = forms.IntegerField(initial=0)
    user_code = forms.CharField(widget=forms.Textarea)


class UserTestCaseForm(forms.Form):
    user_practice = forms.IntegerField()
    testcase = forms.IntegerField()
    is_correct = forms.BooleanField(required=False)
    user_output = forms.CharField(widget=forms.Textarea)


class CodeSubmitForm(forms.Form):
    user_code = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Nhập code của bạn ở đây...'
        }),
        label="Code của bạn"
    )