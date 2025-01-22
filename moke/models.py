from django.db import models
from django.contrib.auth.models import User

class Test(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    image = models.ImageField(upload_to='questions/', blank=True, null=True)
    is_mcq = models.BooleanField(default=True)  # Flag to distinguish question type
    correct_answer = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Question {self.id} for {self.test.title}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Answer {self.id} for Question {self.question.id}"


class TestAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_attempts')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)  # To track completion time
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Attempt by {self.user.username} for {self.test.title}"


class QuestionAttempt(models.Model):
    test_attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='question_attempts')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='attempts')
    selected_answer = models.ForeignKey(Answer, on_delete=models.SET_NULL, blank=True, null=True, related_name='selected_answers')
    answer_text = models.TextField(blank=True, null=True)  # For non-MCQ answers
    status = models.CharField(
        max_length=20,
        choices=[
            ('unanswered', 'Unanswered'),
            ('answered', 'Answered'),
            ('marked_for_review', 'Marked for Review'),
        ],
        default='unanswered'
    )

    def __str__(self):
        return f"Attempt for Question {self.question.id} in Test {self.test_attempt.test.title}"
