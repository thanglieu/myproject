import os
import docker
from django.shortcuts import get_object_or_404, redirect, render

from blog.models import User
from django.core.paginator import Paginator
from .forms import CodeSubmitForm, TestCaseForm, PracticeForm
from .models import Practice, TestCase, UserPractice
from django.forms import formset_factory, inlineformset_factory

# Khởi tạo client Docker
client = docker.from_env()

# chạy code
def run_code_1(lang, code: str, input: str = '' ):
    output, error = "", ""
    code = f"input = {repr(input)}\n{code}"     # repr để xử lý lỗi thừ \n

    # làm sạch lang (ngôn ngữ lập trình)
    lang = lang.lower().strip()

    try:
        if(lang == "python"):
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

        elif(lang == "c++"):
            # Ghi code ra file main.cpp
            filepath = os.path.join(os.getcwd(), "main.cpp")
            with open(filepath, "w") as f:
                f.write(code)

            # Tạo và chạy container C++
            container = client.containers.run(
                image="gcc:latest",   # image có sẵn g++ compiler
                command=["bash", "-c",
                        "g++ /app/main.cpp -o /app/main && echo '{}' | /app/main".format(input)],
                volumes={os.getcwd(): {"bind": "/app", "mode": "rw"}},
                remove=False,
                mem_limit="256m",
                network_disabled=True,
                detach=True
            )
        
        elif(lang == "java"):
            # Ghi code ra file Main.java
            filepath = os.path.join(os.getcwd(), "Main.java")
            with open(filepath, "w") as f:
                f.write(code)

            # Tạo và chạy container Java
            container = client.containers.run(
                image="openjdk:17",   # hoặc openjdk:11 tùy bạn
                command=["bash", "-c", 
                        "javac /app/Main.java && echo '{}' | java -cp /app Main".format(input)],
                volumes={os.getcwd(): {"bind": "/app", "mode": "rw"}},
                remove=False,
                mem_limit="256m",
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

def run_code(lang, code: str, input: str = ''):
    output, error = "", ""
    lang = lang.lower().strip()

    try:
        if lang == "python":
            filepath = os.path.join(os.getcwd(), "temp_code.py")
            with open(filepath, "w") as f:
                f.write(code)

            # tạo container nền (chỉ một lần, có thể giữ lâu)
            container = client.containers.run(
                image="python:3.10",
                command="sleep infinity",
                volumes={os.getcwd(): {"bind": "/app", "mode": "rw"}},
                remove=False,
                mem_limit="128m",
                network_disabled=True,
                detach=True
            )

            # chạy code bên trong container
            exit_code, result = container.exec_run(
                cmd=["python", "/app/temp_code.py"],
                stdin=True,
                stdout=True,
                stderr=True
            )
            output = result.decode()

        elif lang == "c++":
            filepath = os.path.join(os.getcwd(), "main.cpp")
            with open(filepath, "w") as f:
                f.write(code)

            container = client.containers.run(
                image="gcc:latest",
                command="sleep infinity",
                volumes={os.getcwd(): {"bind": "/app", "mode": "rw"}},
                remove=False,
                mem_limit="256m",
                network_disabled=True,
                detach=True
            )

            # compile một lần
            container.exec_run("g++ /app/main.cpp -o /app/main")

            # chạy binary với input
            exit_code, result = container.exec_run(
                cmd=["bash", "-c", f"/app/main"],
                stdin=True,
                stdout=True,
                stderr=True
            )
            output = result.decode()

        elif lang == "java":
            filepath = os.path.join(os.getcwd(), "Main.java")
            with open(filepath, "w") as f:
                f.write(code)

            container = client.containers.run(
                image="openjdk:17",
                command="sleep infinity",
                volumes={os.getcwd(): {"bind": "/app", "mode": "rw"}},
                remove=False,
                mem_limit="256m",
                network_disabled=True,
                detach=True
            )

            # compile một lần
            container.exec_run("javac /app/Main.java")

            # chạy class với input
            exit_code, result = container.exec_run(
                cmd=["java", "-cp", "/app", "Main"],
                stdin=True,
                stdout=True,
                stderr=True
            )
            output = result.decode()

        # dọn dẹp container sau khi xong
        container.remove(force=True)

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
    k = 0   # đánh dấu là create hay confirm. Nếu là confirm thì template phải thêm output
    language = ''

    if request.method == 'POST':
        # gửi code và input nhưng chưa lưu vội, chạy thử trước để xem output
        if request.POST.get('submit') == 'create':
            k = 1
            form = PracticeForm(request.POST)
            formset = TestCaseFormSet(request.POST)
            
            language = request.POST.get('language_type')

            if form.is_valid() and formset.is_valid():
                code_str = form.cleaned_data['code']
                for f in formset:
                    if f.cleaned_data:
                        inp = f.cleaned_data['input']
                        out, err = run_code(language, code_str, inp)
                        # gán output vào INSTANCE để hiển thị trong form CHỨ KHÔNG GÁN VÀO FORM ĐƯỢC
                        f.instance.output = out
  

        # lưu vào DB nếu người tạo thấy output chính xác
        elif request.POST.get('submit') == 'confirm':
            form = PracticeForm(request.POST)
            formset = TestCaseFormSet(request.POST)
            language = request.POST.get('language_type')

            if form.is_valid() and formset.is_valid():
                practice = Practice.objects.create(
                    title=form.cleaned_data['title'],
                    content=form.cleaned_data['content'],
                    code=form.cleaned_data['code'],
                    author=request.user
                )
                practice.topic.set(form.cleaned_data['topic'])

                formset.instance = practice
                # chạy code để lưu output cho từng test case
                for f in formset:
                    if f.cleaned_data:
                        inp = f.cleaned_data['input']
                        out, err = run_code(language, practice.code, inp)
                        TestCase.objects.create(
                            practice=practice,
                            stt=f.cleaned_data['stt'],
                            input=f.cleaned_data['input'],
                            output=out
                        )

                return redirect('practice:practice_list')  
                         

    else:
        form = PracticeForm()
        formset = TestCaseFormSet(initial=question_initial)

    return render(
        request,
        "create.html",
        {'form': form, 'formset': formset, 'k': k, 'language' : language }
    )


# làm practice
def take_practice(request, practice_id):
    practice = get_object_or_404(Practice, id=practice_id)
    testcases = TestCase.objects.filter(practice=practice)

    mark = 0
    user_outputs = []
    user_code = None
    language = None
    k = 0   # đánh dấu code hiện tại là gửi từ POST request (1) hay lấy code trước đó từ trong CSDL (0)

    # nếu là GET request : lấy code cũ trong Practice nếu có
    if request.method == 'GET':
        user_practice = UserPractice.objects.filter(user=request.user, practice=practice).first()
        form = CodeSubmitForm(data={'user_code': user_practice.user_code if user_practice else ''})
        if user_practice:
            user_code = user_practice.user_code
            language = user_practice.language

    # nếu là POST request : lấy code mới người dùng nhập vào
    elif request.method == "POST":
        k = 1
        form = CodeSubmitForm(request.POST)
        if form.is_valid():
            user_code = form.cleaned_data['user_code']
            language = request.POST.get('language_type')

 
    # chạy code trên từng testcase
    if user_code:
        print(user_code)
        for tc in testcases:
            my_out, err = run_code(language, user_code, tc.input)
            is_correct = (my_out.strip() == tc.output.strip())
            if is_correct:
                mark += 1

            user_outputs.append({
                'input': tc.input,
                'expected': tc.output,
                'user_output': my_out,
                'is_correct': is_correct
            })

    # nếu là POST request thì cập nhật code mới vào CSDL
    if request.method == "POST":
        UserPractice.objects.update_or_create(
            user=request.user,
            practice=practice,
            defaults={
                'mark': mark,
                'user_code': user_code, 
                'language': language,
            }
        )


    return render(request, "take_practice.html", {
        "k": k,
        "user_code": user_code,
        "practice": practice,
        "form": form,
        "user_outputs": user_outputs,
        "mark": mark
    })


# danh sách practice - trang chủ
def practice_list(request):
    practices = Practice.objects.all().order_by('-id')  # lấy tất cả, mới nhất trước

    # phân trang
    paginator = Paginator(practices , 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "practice_home.html", {"practices": page_obj})


# danh sách user làm practice
def user_practice_list(request, practice_id):
    practice = get_object_or_404(Practice, id=practice_id)
    user_practices = UserPractice.objects.filter(practice=practice)

    return render(
        request,
        "user_practice.html",
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

    mark = 0
    user_outputs = []
    user_code = None
    language = None

    # nếu là GET request : lấy code cũ trong Practice nếu có
    if request.method == 'GET':
        user_practice = UserPractice.objects.filter(user=request.user, practice=practice).first()
        form = CodeSubmitForm(data={'user_code': user_practice.user_code if user_practice else ''})
        if user_practice:
            user_code = user_practice.user_code
            language = user_practice.language

 
    # chạy code trên từng testcase
    if user_code:
        print(user_code)
        for tc in testcases:
            my_out, err = run_code(language, user_code, tc.input)
            is_correct = (my_out.strip() == tc.output.strip())
            if is_correct:
                mark += 1

            user_outputs.append({
                'input': tc.input,
                'expected': tc.output,
                'user_output': my_out,
                'is_correct': is_correct
            })

    return render(request, "take_practice.html", {
        "user_code": user_code,
        "practice": practice,
        "form": form,
        "user_outputs": user_outputs,
        "mark": mark,
        "m" : 1,    # đánh dấu là xem code của người khác
    })
