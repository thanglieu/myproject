from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.forms import formset_factory, inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AnswerForm, QuestionCountForm, QuestionForm, TestForm
from .models import Answer, Question, Test, UserAnswer, UserTest

User = get_user_model()

# chọn số lượng Form, tiêu đề title để bước sau tạo Test
@login_required(login_url='/blog/login/')
def create_test_count(request):
    # Hiển thị form để chọn số lượng câu hỏi cho bài kiểm tra mới
    form = QuestionCountForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        title = form.cleaned_data['title']
        question_count = form.cleaned_data['question_count']
        return redirect('exam:create_test', question_count=question_count, title=title)

    return render(request, 'create_count.html', {'form': form})



# tạo Test - nhập liệu Form
@login_required(login_url='/blog/login/')
def create_test(request, question_count, title):
    question_count = int(question_count)

    QuestionFormSet = inlineformset_factory(
        Test,
        Question,
        form=QuestionForm,
        extra=question_count,
        min_num=question_count,
        max_num=question_count,
        validate_min=True,
        validate_max=True,
        can_delete=False,
    )
    AnswerFormSet = formset_factory(
        AnswerForm,
        extra=4,
        min_num=4,
        max_num=4,
        validate_min=True,
        validate_max=True,
    )

    question_initial = [{'stt': i + 1} for i in range(question_count)]
    answer_initial = [{'title': chr(97 + i)} for i in range(4)]

    if request.method == 'POST':
        question_formset = QuestionFormSet(
            request.POST,
            prefix='questions',
            instance=Test(),
        )
        answer_formsets = [
            AnswerFormSet(request.POST, prefix=f'answers-{idx}')
            for idx in range(question_count)
        ]

        if (
        #    test_form.is_valid() and 
            question_formset.is_valid()
            and all(fs.is_valid() for fs in answer_formsets)
        ):
            with transaction.atomic():
                # tạo Test dựa trên dữ liệu ở bước trước
                test = Test.objects.create(
                    title=title,
                    quantity=question_count,
                    author=request.user
                )

                for index, question_form in enumerate(question_formset):
                    question = question_form.save(commit=False)
                    question.test = test
                    question.save()

                    for answer_form in answer_formsets[index]:
                        answer = answer_form.save(commit=False)
                        answer.question = question
                        answer.save()

            return redirect('exam:exam_home')
    else:
    #    test_form = TestForm()
        question_formset = QuestionFormSet(
            prefix='questions',
            instance=Test(),
            initial=question_initial,
        )
        answer_formsets = [
            AnswerFormSet(prefix=f'answers-{idx}', initial=answer_initial)
            for idx in range(question_count)
        ]

    # kết hợp Question form và Answer Formset thành từng cặp để hiển thị 
    question_answer_pairs = list(zip(question_formset.forms, answer_formsets))

    return render( request,'create_test.html',{
            'question_formset': question_formset,
            'answer_formsets': answer_formsets,
            'question_answer_pairs': question_answer_pairs,
            'question_count': question_count,
            'title' : title,
        }
    )





# trang chủ - tìm kiếm
def exam_home(request):
    """Tìm kiếm bài kiểm tra theo từ khóa trong tiêu đề."""
    query = request.GET.get('q', '').strip()
    tests = Test.objects.order_by('-id')
    if query:
        tests = tests.filter(title__icontains=query)

    return render(request, 'exam_home.html', {'tests': tests, 'query': query, 'this_user_id': request.user.id })


# hiển thị Test của User khác
def user_tests(request, user_id):
    author = get_object_or_404(User, pk=user_id)
    tests = Test.objects.filter(author=author).order_by('-id')
    return render(request, 'user_tests_list.html', {'tests': tests, 'author': author})


# làm Test
@login_required(login_url='/blog/login/')
def take_test(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    questions = Question.objects.filter(test=test).order_by('stt', 'id')
    error = None
    
    # nếu lần trước đã làm
    existing_user_test = UserTest.objects.filter(user=request.user, test=test).first()

    if request.method == 'POST':
        # lấy danh sách Answer được User chọn
        selected_answers = {}

        for question in questions:
            # lấy id của Answer được chọn (Answer được selected trong số 4 Answer)
            selected = request.POST.get(f'question_{question.id}')

            # thêm vào dict
            if selected:
                selected_answers[str(question.id)] = selected

        # phải chọn Answer cho toàn bộ Question
        if len(selected_answers) != questions.count():
            error = 'Vui lòng chọn đáp án cho tất cả câu hỏi.'
        else:
            with transaction.atomic():
                # tạo mới hoặc cật nhật bài đã làm 
                user_test, _ = UserTest.objects.get_or_create(user=request.user, test=test)
                # xóa hết toàn bộ đáp án cũ nếu là 'cập nhật'
                UserAnswer.objects.filter(test=user_test).delete()

                # tính điểm
                correct_count = 0
                for question in questions:
                    # lấy đáp án được chọn
                    answer_id = int(selected_answers[str(question.id)])
                    answer = get_object_or_404(Answer, pk=answer_id, question=question)
                    
                    # lưu vào UserAnswer (Question có 4 Answer nhưng chỉ lưu Answer được chọn vào UserANsswer)
                    UserAnswer.objects.create(test=user_test, answer=answer)

                    # cộng điểm nếu đáp án đúng

                    if answer.is_correct:
                        correct_count += 1

                # lưu điểm
                user_test.score = round(correct_count / questions.count() * 100, 2)
                user_test.save()

            return redirect('exam:user_answer', user_test_id=user_test.id)

    return render(request, 'take_test.html', {
            'test': test,
            'questions': questions,
            'existing_user_test': existing_user_test,
            'error': error,
        }
    )


@login_required(login_url='/blog/login/')
def user_answer(request, user_test_id):
    # Hiển thị chi tiết kết quả cho một lần làm bài cụ thể
    user_test = get_object_or_404(UserTest, pk=user_test_id, user=request.user)
    answers = UserAnswer.objects.filter(test=user_test).select_related('answer__question')
    selected_by_question = {ua.answer.question.id: ua.answer for ua in answers}

    questions = Question.objects.filter(test=user_test.test).order_by('stt', 'id')
    question_results = []
    for question in questions:
        answer = selected_by_question.get(question.id)
        question_results.append({'question': question, 'answer_list':Answer.objects.filter(question=question).order_by('id'), 'answer': answer})

    return render(
        request, 'user_answer.html', {
            'user_test': user_test,
            'question_results': question_results,
        }
    )
