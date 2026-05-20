import os
import docker
from django.shortcuts import get_object_or_404, redirect, render

from blog.models import User

from .forms import CodeSubmitForm, TestCaseForm, PracticeForm
from .models import Practice, TestCase, UserPractice
from django.forms import formset_factory, inlineformset_factory

# Khởi tạo client Docker
client = docker.from_env()

# chạy code
def run_code(code: str, input: str = '' ):
    output, error = "", ""
    code = f"input = {repr(input)}\n{code}"     # repr để xử lý lỗi thừ \n
    try:
        # Ghi code ra file tạm
        filepath = os.path.join(os.getcwd(), "temp_code.py")
        with open(filepath, "w") as f:
            f.write(code)

        # Tạo và chạy container
        container = client.containers.run(
            image="python:3.10",
            command=["python", "/app/temp_code.py"],
            volumes={os.getcwd(): {"bind": "/app", "mode": "rw"}},
            remove=False,
            mem_limit="128m",
            network_disabled=True,
            detach=True
        )

        # Chờ container kết thúc
        container.wait()

        # Lấy log
        result = container.logs(stdout=True, stderr=True)
        output = result.decode("utf-8")

        # Xóa container
        container.remove()

    except docker.errors.ContainerError as e:
        error = str(e)
    except Exception as e:
        error = str(e)

    return output, error


#online code runner
def run_practice(request):
    output, error, input, code = "", "", "", ""
    if request.method == "POST":
        input = request.POST.get('input')
        code = request.POST.get('code')
        output, error = run_code(code, input)
        # Debug ra console
        print([output, error])

    # Render ra giao diện
    return render(request, "runner.html", {"input": input, "output": output, "error": error, "code": code})


# tạo practice
def create_practice(request):
    TestCaseFormSet = inlineformset_factory(
        Practice,
        TestCase,
        form=TestCaseForm,
        fields=['stt', 'input','output'],   # chỉ rõ fields
        extra=5,
        can_delete=False
    )

    question_initial = [{'stt': i + 1} for i in range(5)]
    k = 0

    if request.method == 'POST':
        # gửi code và input nhưng chưa lưu vội, chạy thử trước để xem output
        if request.POST.get('submit') == 'create':
            k = 1
            form = PracticeForm(request.POST)
            formset = TestCaseFormSet(request.POST)

            if form.is_valid() and formset.is_valid():
                code_str = form.cleaned_data['code']
                for f in formset:
                    if f.cleaned_data:
                        inp = f.cleaned_data['input']
                        out, err = run_code(code_str, inp)
                        # gán output vào INSTANCE để hiển thị trong form CHỨ KHÔNG GÁN VÀO FORM ĐƯỢC
                        f.instance.output = out


        # lưu vào DB nếu người tạo thấy output chính xác
        elif request.POST.get('submit') == 'confirm':
            form = PracticeForm(request.POST)
            formset = TestCaseFormSet(request.POST)
            if form.is_valid() and formset.is_valid():
                practice = Practice.objects.create(
                    title=form.cleaned_data['title'],
                    content=form.cleaned_data['content'],
                    code=form.cleaned_data['code'],
                    author=request.user
                )
                formset.instance = practice
                # chạy code để lưu output cho từng test case
                for f in formset:
                    if f.cleaned_data:
                        inp = f.cleaned_data['input']
                        out, err = run_code(practice.code, inp)
                        TestCase.objects.create(
                            practice=practice,
                            stt=f.cleaned_data['stt'],
                            input=f.cleaned_data['input'],
                            output=out
                        )

                return redirect('practice:run_code')  # hoặc trang bạn muốn
                         

    else:
        form = PracticeForm()
        formset = TestCaseFormSet(initial=question_initial)

    return render(
        request,
        "create.html",
        {'form': form, 'formset': formset, 'k': k }
    )


# làm practice
def take_practice(request, practice_id):
    practice = get_object_or_404(Practice, id=practice_id)
    testcases = TestCase.objects.filter(practice=practice)

    mark = 0
    user_outputs = []

    if request.method == "POST":
        form = CodeSubmitForm(request.POST)

        if form.is_valid():
            user_code = form.cleaned_data['user_code']

            # chạy code trên từng testcase
            for tc in testcases:
                out, err = run_code(user_code, tc.input)
                is_correct = (out.strip() == tc.output.strip())
                if is_correct:
                    mark += 1

                user_outputs.append({
                    'input': tc.input,
                    'expected': tc.output,
                    'user_output': out,
                    'is_correct': is_correct
                })

            UserPractice.objects.update_or_create(
                user=request.user,
                practice=practice,
                defaults={
                    'mark': mark,
                    'user_code': user_code
                }
            )

    else:
        form = CodeSubmitForm()

    return render(request, "take_practice.html", {
        "practice": practice,
        "form": form,
        "user_outputs": user_outputs,
        "mark": mark
    })


# danh sách practice
def practice_list(request):
    practices = Practice.objects.all().order_by('-id')  # lấy tất cả, mới nhất trước
    return render(request, "practice_list.html", {"practices": practices})


# danh sách user làm practice
def user_practice_list(request, practice_id):
    practice = get_object_or_404(Practice, id=practice_id)
    user_practices = UserPractice.objects.filter(practice=practice)

    return render(
        request,
        "user_practice_list.html",
        {
            "practice": practice,
            "user_practices": user_practices,
        }
    )


# chi tiết user làm practice
def user_practice(request, practice_id, user_id):
    practice = get_object_or_404(Practice, id=practice_id)
    user = get_object_or_404(User, id=user_id)
    user_practice = get_object_or_404(UserPractice, practice=practice, user=user)
    testcases = TestCase.objects.filter(practice=practice)

    user_outputs = []
    for tc in testcases:
        out, err = run_code(user_practice.user_code, tc.input)
        user_outputs.append({
            'input': tc.input,
            'expected': tc.output,
            'user_output': out,
            'is_correct': (out.strip() == tc.output.strip())
        })

    return render(request, "user_practice.html", {
        "practice": practice,
        "user": user,
        "user_practice": user_practice,
        "user_outputs": user_outputs
    })




