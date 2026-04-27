from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.forms import formset_factory
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AnswerForm, QuestionCountForm, QuestionForm, TestForm
from .models import Answer, Question, Test, UserAnswer, UserTest

User = get_user_model()


@login_required(login_url='/blog/login/')
def create_test_count(request):
    # Hiển thị form để chọn số lượng câu hỏi cho bài kiểm tra mới
    form = QuestionCountForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        question_count = form.cleaned_data['question_count']
        return redirect('exam:create_test', question_count=question_count)

    return render(request, 'create_count.html', {'form': form})


@login_required(login_url='/blog/login/')
def create_test(request, question_count):
    """Tạo bài kiểm tra mới và lưu test, câu hỏi cùng đáp án vào database."""
    QuestionFormSet = formset_factory(
        QuestionForm,
        extra=question_count,
        min_num=question_count,
        max_num=question_count,
        validate_min=True,
        validate_max=True,
    )
    AnswerFormSet = formset_factory(
        AnswerForm,
        extra=4,
        min_num=4,
        max_num=4,
        validate_min=True,
        validate_max=True,
    )

    if request.method == 'POST':
        test_form = TestForm(request.POST)
        question_formset = QuestionFormSet(request.POST, prefix='questions')
        answer_formsets = [
            AnswerFormSet(request.POST, prefix=f'answers-{idx}')
            for idx in range(question_count)
        ]

        if test_form.is_valid() and question_formset.is_valid() and all(fs.is_valid() for fs in answer_formsets):
            with transaction.atomic():
                test = test_form.save(commit=False)
                test.author = request.user
                test.save()

                for index, question_form in enumerate(question_formset):
                    question = question_form.save(commit=False)
                    question.test = test
                    question.save()

                    for answer_form in answer_formsets[index]:
                        answer = answer_form.save(commit=False)
                        answer.question = question
                        answer.save()

            return redirect('exam:my_tests')
    else:
        test_form = TestForm()
        question_formset = QuestionFormSet(prefix='questions')
        answer_formsets = [AnswerFormSet(prefix=f'answers-{idx}') for idx in range(question_count)]

    question_answer_pairs = list(zip(question_formset.forms, answer_formsets))

    return render(
        request,
        'exam/create_test.html',
        {
            'test_form': test_form,
            'question_formset': question_formset,
            'answer_formsets': answer_formsets,
            'question_answer_pairs': question_answer_pairs,
            'question_count': question_count,
        }
    )


def search_tests(request):
    """Tìm kiếm bài kiểm tra theo từ khóa trong tiêu đề."""
    query = request.GET.get('q', '').strip()
    tests = Test.objects.order_by('-id')
    if query:
        tests = tests.filter(title__icontains=query)

    return render(request, 'search_tests.html', {'tests': tests, 'query': query})


@login_required(login_url='/blog/login/')
def my_tests(request):
    """Hiển thị danh sách các bài kiểm tra mà người dùng hiện tại đã tạo."""
    tests = Test.objects.filter(author=request.user).order_by('-id')

    for t in tests:
        # Với mỗi test, lấy danh sách các lần làm bài để hiển thị điểm.
        t.takers = UserTest.objects.filter(test=t).select_related('user').order_by('-score')
    return render(request, 'my_tests.html', {'tests': tests})


def user_tests(request, user_id):
    """Hiển thị các bài kiểm tra của một tác giả khác."""
    author = get_object_or_404(User, pk=user_id)
    tests = Test.objects.filter(author=author).order_by('-id')
    return render(request, 'user_tests.html', {'tests': tests, 'author': author})


@login_required(login_url='/blog/login/')
def take_test(request, test_id):
    """Cho phép người dùng làm bài kiểm tra và lưu kết quả của họ."""
    test = get_object_or_404(Test, pk=test_id)
    questions = Question.objects.filter(test=test).order_by('stt', 'id')
    existing_user_test = UserTest.objects.filter(user=request.user, test=test).first()
    error = None

    if request.method == 'POST':
        selected_answers = {}
        for question in questions:
            selected = request.POST.get(f'question_{question.id}')
            if selected:
                selected_answers[str(question.id)] = selected

        if len(selected_answers) != questions.count():
            error = 'Vui lòng chọn đáp án cho tất cả câu hỏi.'
        else:
            with transaction.atomic():
                user_test, _ = UserTest.objects.get_or_create(user=request.user, test=test)
                UserAnswer.objects.filter(test=user_test).delete()

                correct_count = 0
                for question in questions:
                    answer_id = int(selected_answers[str(question.id)])
                    answer = get_object_or_404(Answer, pk=answer_id, question=question)
                    UserAnswer.objects.create(test=user_test, answer=answer)
                    if answer.is_correct:
                        correct_count += 1

                user_test.score = round(correct_count / questions.count() * 100, 2)
                user_test.save()

            return redirect('exam:test_result', user_test_id=user_test.id)

    return render(
        request,
        'take_test.html',
        {
            'test': test,
            'questions': questions,
            'existing_user_test': existing_user_test,
            'error': error,
        }
    )


@login_required(login_url='/blog/login/')
def test_result(request, user_test_id):
    """Hiển thị chi tiết kết quả cho một lần làm bài cụ thể."""
    user_test = get_object_or_404(UserTest, pk=user_test_id, user=request.user)
    answers = UserAnswer.objects.filter(test=user_test).select_related('answer__question')
    selected_by_question = {ua.answer.question.id: ua.answer for ua in answers}

    questions = Question.objects.filter(test=user_test.test).order_by('stt', 'id')
    question_results = []
    for question in questions:
        answer = selected_by_question.get(question.id)
        question_results.append({'question': question, 'answer': answer})

    return render(
        request,
        'test_result.html',
        {
            'user_test': user_test,
            'question_results': question_results,
        }
    )
