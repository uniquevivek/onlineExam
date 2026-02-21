from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
from exam.models import ExamSchedule, ExamAttempt, Question



def student_dashboard(request):
    user = request.user
    now = timezone.localtime()

    schedules = ExamSchedule.objects.filter(
        group__students=user,
        is_cancelled=False
    ).select_related("exam", "group")

    exam_list = []

    for schedule in schedules:

        exam_datetime_start = datetime.combine(schedule.date, schedule.start_time)
        exam_datetime_end = datetime.combine(schedule.date, schedule.end_time)

        # Make them naive to match now
        exam_datetime_start = exam_datetime_start.replace(tzinfo=None)
        exam_datetime_end = exam_datetime_end.replace(tzinfo=None)

        current_time = now.replace(tzinfo=None)

        attempt_submitted = ExamAttempt.objects.filter(
            student=user,
            schedule=schedule,
            is_submitted=True
        ).exists()

        if attempt_submitted:
            status = "Completed"

        elif current_time < exam_datetime_start:
            status = "Upcoming"

        elif exam_datetime_start <= current_time <= exam_datetime_end:
            status = "Instructions"   # 👈 change here

        else:
            status = "Expired"


        print("FINAL STATUS:", status)

        exam_list.append({
            "schedule": schedule,
            "status": status,
            "is_live": status == "Live",
            "is_instruction": status == "Instructions",
            "is_completed": status == "Completed",
            "is_upcoming": status == "Upcoming",
            "is_expired": status == "Expired",
        })


    # Notices (for now simple upcoming today)
    today_exams = [
        exam for exam in exam_list
        if exam["schedule"].date == now.date()
        and exam["status"] in ["Upcoming", "Instructions", "Live"]
    ]
    results = ExamAttempt.objects.filter(
    student=user,
    is_submitted=True
    ).select_related("schedule__exam").order_by("-submitted_at")


    context = {
        "exam_list": exam_list,
        "today_exams": today_exams,
        "results": results,
    }

    return render(request, "student//student_dashboard.html", context)

from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from datetime import datetime, timedelta
from exam.models import ExamSchedule, ExamAttempt


def start_exam(request, schedule_id):
    schedule = get_object_or_404(
        ExamSchedule,
        id=schedule_id,
        group__students=request.user,
        is_cancelled=False
    )

    now = timezone.localtime()

    start_datetime = timezone.make_aware(
        datetime.combine(schedule.date, schedule.start_time)
    )
    end_datetime = timezone.make_aware(
        datetime.combine(schedule.date, schedule.end_time)
    )

    # 🚨 Security Check
    if now < start_datetime - timedelta(minutes=10):
        return redirect("core:student_dashboard")

    if now > end_datetime:
        return redirect("core:student_dashboard")

    attempt, created = ExamAttempt.objects.get_or_create(
        student=request.user,
        schedule=schedule
    )

    if attempt.is_submitted:
        return redirect("core:student_dashboard")

    remaining_seconds = int((end_datetime - now).total_seconds())

    questions = schedule.exam.questions.all()

    return render(request, "student/exam_page.html", {
        "schedule": schedule,
        "remaining_seconds": remaining_seconds,
        "questions": questions
    })

# from django.utils import timezone


# def submit_exam(request, schedule_id):
#     schedule = get_object_or_404(ExamSchedule, id=schedule_id)

#     attempt = get_object_or_404(
#         ExamAttempt,
#         student=request.user,
#         schedule=schedule
#     )

#     if not attempt.is_submitted:
#         attempt.is_submitted = True
#         attempt.submitted_at = timezone.now()
#         attempt.save()

#     return redirect("core:student_dashboard")

from django.http import JsonResponse
from exam.models import StudentAnswer, ExamAttempt, ExamSchedule, Question


def save_answer(request):
    if request.method == "POST":
        question_id = request.POST.get("question_id")
        selected_option = request.POST.get("selected_option")
        schedule_id = request.POST.get("schedule_id")

        schedule = ExamSchedule.objects.get(id=schedule_id)

        attempt = ExamAttempt.objects.get(
            student=request.user,
            schedule=schedule,
            is_submitted=False
        )

        question = Question.objects.get(id=question_id)

        StudentAnswer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={"selected_option": selected_option}
        )

        return JsonResponse({"status": "saved"})


from exam.models import StudentAnswer

def submit_exam(request, schedule_id):
    schedule = get_object_or_404(ExamSchedule, id=schedule_id)

    attempt = get_object_or_404(
        ExamAttempt,
        student=request.user,
        schedule=schedule,
        is_submitted=False
    )

    answers = StudentAnswer.objects.filter(attempt=attempt)

    total_score = 0

    for answer in answers:
        if answer.selected_option == answer.question.correct_option:
            total_score += answer.question.marks

    attempt.score = total_score
    attempt.is_submitted = True
    attempt.submitted_at = timezone.now()
    attempt.save()

    return redirect("student:result_view", schedule_id=schedule.id)


def exam_instructions(request, schedule_id):
    schedule = get_object_or_404(
        ExamSchedule,
        id=schedule_id,
        group__students=request.user
    )

    return render(request, "student/exam_instructions.html", {
        "schedule": schedule
    })

def result_view(request, schedule_id):
    attempt = get_object_or_404(
        ExamAttempt,
        student=request.user,
        schedule_id=schedule_id,
        is_submitted=True
    )

    return render(request, "student/result.html", {
        "attempt": attempt
    })

