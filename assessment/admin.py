from django.contrib import admin
from .models import (MultiChoiceQuestion, Question, QuestionGroup,
                     AssessmentPreference, StudentMultiChoiceAnswer, MultiChoiceScripts,
                     )


@admin.register(Question)
class QuestionModelAdmin(admin.ModelAdmin):
    list_filter = ("group", )
    list_display = ("question_title", "max_mark", "type_")
    readonly_fields = ("group", )

    def type_(self, obj:Question):
        return "Multi Choice Question" if obj.multichoicequestion_set.exists() else "Theoretical"

    def question_title(self, question):
        if len(str(question)) > 100:
            return str(question)[:100] + "..."
        else:
            return str(question)


@admin.register(QuestionGroup)
class QuestionGroupModelAdmin(admin.ModelAdmin):
    list_display = ("course",  "title")
    list_filter = ("title", )
    ordering = ("title", "course")
    readonly_fields = ("preference", "course")


@admin.register(MultiChoiceQuestion)
class MultiChoiceQuestionModelAdmin(admin.ModelAdmin):
    list_display = ("option", "question_title", "is_answer_option")
    readonly_fields = ("question", )

    def question_title(self, MultiChoiceQuestion):
        if len(MultiChoiceQuestion.question.question) > 100:
            return str(MultiChoiceQuestion.question.question)[:100] + "..."
        else:
            return MultiChoiceQuestion.question.question

    def get_queryset(self, request):
        return MultiChoiceQuestion.objects.filter(is_answer_option=True)


@admin.register(AssessmentPreference)
class AssessmentPreferenceModelAdmin(admin.ModelAdmin):
    list_display = ("duration", "due_date", "environment", "is_question_shuffle")


@admin.register(StudentMultiChoiceAnswer)
class StudentMultiChoiceAnswerModelAdmin(admin.ModelAdmin):
    list_display = ("question", "selected_option",)
    readonly_fields = ("question", "selected_option", "script")


@admin.register(MultiChoiceScripts)
class MultiChoiceScriptsModelAdmin(admin.ModelAdmin):
    list_display = ("__str__", "score", "Start_Date_Time",
                    "is_completed", "is_canceled", "has_paused")

    readonly_fields = ("student", "course", "question_group", "score")

    def Start_Date_Time(self, instance):
        return instance.timestamp
