from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .form import CustomUserForm
from .models import Test, Question, Answer, TestAttempt, QuestionAttempt
from urllib.parse import urlencode

# Home view
def home(request):
    return render(request, "moke/index.html")

# View to list all available tests
def test_list(request):
    tests = Test.objects.all()
    return render(request, 'moke/test_list.html', {'tests': tests})

# Login view
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
        else:
            messages.error(request, "Invalid credentials")
    else:
        form = AuthenticationForm()

    return render(request, 'moke/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('home')

# Register view
def register(request):
    form = CustomUserForm()
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('/login')
    return render(request, "moke/register.html", {'form': form})

@login_required
def take_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    test_attempt, created = TestAttempt.objects.get_or_create(user=request.user, test=test)

    # Retrieve all questions for the test
    questions = list(test.questions.all())
    total_questions = len(questions)

    # Get the current question index
    current_index = int(request.GET.get('index', request.session.get(f'test_{test_id}_current_index', 0)))
    if current_index < 0 or current_index >= total_questions:
        current_index = 0
    question = questions[current_index]

    # Get or create the question attempt
    question_attempt, created = QuestionAttempt.objects.get_or_create(
        test_attempt=test_attempt,
        question=question,
        defaults={'status': 'unanswered'}
    )

    # Handle POST request for answer submission
    if request.method == 'POST':
        user_answer = request.POST.get('answer')

        # Save the user's answer
        if user_answer:
            if question.is_mcq:
                try:
                    selected_answer = Answer.objects.get(id=user_answer)
                    question_attempt.selected_answer = selected_answer
                    question_attempt.status = 'answered'
                except Answer.DoesNotExist:
                    messages.error(request, "Invalid answer. Please select a valid option.")
            else:
                question_attempt.answer_text = user_answer.strip()
                question_attempt.status = 'answered'
            question_attempt.save()

        # Handle navigation
        if 'mark_review' in request.POST:
            question_attempt.status = 'marked_for_review'
            question_attempt.save()
        
        if 'next' in request.POST and current_index < total_questions - 1:
            current_index += 1
        elif 'previous' in request.POST and current_index > 0:
            current_index -= 1

        # Save the updated index in the session
        request.session[f'test_{test_id}_current_index'] = current_index

        # Handle form submission
        if 'submit' in request.POST:
            return redirect('test_completed', test_id=test_id)

        # Save remaining time on form submission
        request.session[f'test_{test_id}_time_remaining'] = request.POST.get('time_remaining', 0)

        # Build URL with updated index as a query parameter
        query_params = urlencode({'index': current_index})
        return redirect(f'{request.path}?{query_params}')

    # Get all question attempts for progress tracking
    all_attempts = QuestionAttempt.objects.filter(test_attempt=test_attempt)
    question_statuses = {
        attempt.question.id: attempt.status for attempt in all_attempts
    }

    # Timer setup (default time is 15 minutes)
    time_remaining = request.session.get(f'test_{test_id}_time_remaining', 900)  # 900 seconds = 15 minutes

    return render(request, 'moke/take_test.html', {
        'test': test,
        'question': question,
        'current_index': current_index,
        'total_questions': total_questions,
        'range_total_questions': range(total_questions),
        'question_statuses': question_statuses,
        'time_remaining': time_remaining,
    })
@login_required
def test_completed(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    test_attempt = get_object_or_404(TestAttempt, user=request.user, test=test)
    question_attempts = test_attempt.question_attempts.all()

    # Initialize score and results
    score = 0
    results = []

    # Iterate through all the question attempts to calculate the score
    for attempt in question_attempts:
        question = attempt.question
        user_answer = (
            attempt.selected_answer.text if question.is_mcq and attempt.selected_answer else attempt.answer_text
        )
        correct_answer = (
            Answer.objects.filter(question=question, is_correct=True).first()
        )

        # For MCQ questions, compare the selected answer with the correct answer
        if question.is_mcq:
            if attempt.selected_answer and correct_answer and attempt.selected_answer.id == correct_answer.id:
                score += 1
        elif user_answer:
            # For non-MCQ questions, compare the user's text answer with the correct answer
            if correct_answer and user_answer.strip().lower() == correct_answer.text.strip().lower():
                score += 1

        # Append the question and answer details to the results list
        results.append({
            'question': question,
            'user_answer': user_answer if user_answer else "No answer selected",
            'correct_answer': correct_answer.text if correct_answer else "No correct answer available",
            'is_correct': (user_answer.strip().lower() == correct_answer.text.strip().lower()) if correct_answer and user_answer else False,
        })

    # Mark the test as completed
    test_attempt.is_completed = True
    test_attempt.save()

    # Render the results page with the score and answers
    return render(request, 'moke/test_results.html', {
        'test': test,
        'score': score,
        'results': results,
    })

