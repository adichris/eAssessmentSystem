from django import template
register = template.Library()


@register.filter(name="get_score")
def get_score(student, question_group):
    return student.get_quiz_script_score(
        question_group_pk=question_group.pk,
        quiz_type=question_group.questions_type,
        q_title=question_group.title
    )


@register.filter(name="get_total_score")
def total_score(student, course):
    return student.get_course_total_score(
        course_code=course.code,
        course_semester=course.semester
    )
