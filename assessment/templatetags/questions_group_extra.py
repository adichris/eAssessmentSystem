from django import template
from assessment.models import Question

register = template.Library()


@register.filter(name="question_text")
def get_question(pk):
    try:
        question = Question.objects.get(pk=pk)
        return question.question
    except Question.DoesNotExist:
        return
