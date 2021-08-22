from django import template
from assessment.models import Question, StudentTheoryAnswer
from django.utils.html import format_html, linebreaks
register = template.Library()


@register.filter(name="question_text")
def get_question(question_tag):
    """ question.value() == question_id"""
    try:
        question = Question.objects.get(pk=question_tag.value())
        return format_html("<div class='d-flex justify-content-between'><p>Question {}</p> <span>{} marks</span> </div> {}",
                           question.question_number,
                           round(question.max_mark, 2),
                           format_html(linebreaks(question.question))
                           )
    except (Question.DoesNotExist, ValueError):
        return


@register.filter(name="is_answered")
def is_solved_by_student(question_id, script_id):
    return StudentTheoryAnswer.objects.is_question_answered(question_id, script_id)
