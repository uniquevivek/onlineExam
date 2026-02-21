from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import teacher_required
from .models import Exam, Question
from .forms import ExamForm, QuestionForm


@teacher_required
@login_required
def exam_list(request):
    exams = Exam.objects.filter(created_by=request.user)
    return render(request, 'exam/exam_list.html', {'exams': exams})

def exam_list(request):
    exams = Exam.objects.filter(created_by=request.user)
    return render(request, 'exam/exam_list.html', {'exams': exams})

@teacher_required
@login_required
def exam_create(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            return redirect('exam:exam_list')
    else:
        form = ExamForm()
    return render(request, 'exam/exam_form.html', {'form': form})

@teacher_required
@login_required
def exam_update(request, pk):
    exam = get_object_or_404(Exam, pk=pk, created_by=request.user)
    form = ExamForm(request.POST or None, instance=exam)
    if form.is_valid():
        form.save()
        return redirect('exam:exam_list')
    return render(request, 'exam/exam_form.html', {'form': form})

@teacher_required
@login_required
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk, created_by=request.user)
    if request.method == 'POST':
        exam.delete()
        return redirect('exam:exam_list')
    return render(request, 'exam/exam_confirm_delete.html', {'exam': exam})

@teacher_required
@login_required
def question_add(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('exam:exam_list')
    else:
        form = QuestionForm(initial={'exam': exam})
    return render(request, 'exam/question_form.html', {'form': form, 'exam': exam})

@teacher_required
@login_required
def question_list(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    questions = exam.questions.all()
    return render(request, 'exam/question_list.html', {
        'exam': exam,
        'questions': questions
    })

@teacher_required
@login_required
def question_update(request, pk):
    question = get_object_or_404(Question, id=pk, exam__created_by=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('exam:uestion_list', exam_id=question.exam.id)
    else:
        form = QuestionForm(instance=question)

    return render(request, 'exam/question_form.html', {
        'form': form,
        'exam': question.exam
    })

# @login_required
# def question_delete(request, pk):
#     question = get_object_or_404(Question, id=pk, exam__created_by=request.user)
#     exam_id = question.exam.id

#     if request.method == 'POST':
#         question.delete()
#         return redirect('question_list', exam_id=exam_id)

#     return render(request, 'exam/question_confirm_delete.html', {
#         'question': question
#     })

@login_required
def question_delete(request, pk):
    question = get_object_or_404(
        Question,
        id=pk,
        exam__created_by=request.user
    )

    exam_id = question.exam.id

    if request.method == 'POST':
        question.delete()
        return redirect('exam:question_list', exam_id=exam_id)

    return redirect('exam:question_list', exam_id=exam_id)


from .forms import StudentGroupForm, ExamScheduleForm
from .models import StudentGroup, ExamSchedule


@login_required
def group_create(request):
    if request.method == "POST":
        form = StudentGroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("exam:group_list")
    else:
        form = StudentGroupForm()

    return render(request, "exam/group_create.html", {"form": form})

@login_required
def group_list(request):
    groups = StudentGroup.objects.all()
    return render(request, "exam/group_list.html", {"groups": groups})

@login_required
def schedule_create(request):
    if request.method == "POST":
        form = ExamScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("exam:schedule_list")
    else:
        form = ExamScheduleForm()

    return render(request, "exam/schedule_create.html", {"form": form})

@login_required
def schedule_list(request):
    schedules = ExamSchedule.objects.filter(is_cancelled=False)
    return render(request, "exam/schedule_list.html", {"schedules": schedules})


from django.shortcuts import get_object_or_404
from django.contrib import messages


@login_required
def schedule_cancel(request, pk):
    schedule = get_object_or_404(ExamSchedule, pk=pk)

    if request.method == "POST":
        schedule.is_cancelled = True
        schedule.save()
        messages.success(request, "Exam schedule cancelled successfully.")
        return redirect("exam:schedule_list")

    return render(request, "exam/schedule_cancel.html", {"schedule": schedule})


@login_required
def schedule_reschedule(request, pk):
    schedule = get_object_or_404(ExamSchedule, pk=pk)

    if schedule.is_cancelled:
        messages.error(request, "Cannot reschedule a cancelled exam.")
        return redirect("exam:schedule_list")

    if request.method == "POST":
        form = ExamScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam rescheduled successfully.")
            return redirect("exam:schedule_list")
    else:
        form = ExamScheduleForm(instance=schedule)

    return render(request, "exam/schedule_reschedule.html", {
        "form": form,
        "schedule": schedule
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from exam.models import ExamSchedule, ExamAttempt


@login_required
def teacher_results(request, schedule_id):

    schedule = get_object_or_404(ExamSchedule, id=schedule_id)

    # 🔐 Security: Only exam creator (teacher) can view results
    if request.user != schedule.exam.created_by:
        raise PermissionDenied

    attempts = ExamAttempt.objects.filter(
        schedule=schedule,
        is_submitted=True
    ).select_related("student")

    results_data = []

    for attempt in attempts:
        total_marks = schedule.exam.total_marks
        percentage = (attempt.score / total_marks) * 100 if total_marks > 0 else 0

        results_data.append({
            "student": attempt.student,
            "score": attempt.score,
            "total_marks": total_marks,
            "percentage": round(percentage, 2),
            "submitted_at": attempt.submitted_at,
        })

    return render(request, "exam/teacher_results.html", {
        "schedule": schedule,
        "results_data": results_data
    })

@login_required
def teacher_all_results(request):

    schedules = ExamSchedule.objects.filter(
        exam__created_by=request.user
    ).select_related("exam")

    return render(request, "exam/teacher_all_results.html", {
        "schedules": schedules
    })

@login_required
def teacher_results(request, schedule_id):

    schedule = get_object_or_404(ExamSchedule, id=schedule_id)

    if request.user != schedule.exam.created_by:
        raise PermissionDenied

    attempts = ExamAttempt.objects.filter(
        schedule=schedule,
        is_submitted=True
    ).select_related("student")

    return render(request, "exam/teacher_results.html", {
        "schedule": schedule,
        "attempts": attempts
    })

