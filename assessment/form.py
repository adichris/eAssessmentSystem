from django import forms
from .models import (
    MultiChoiceQuestion, Question, QuestionGroup,
    AssessmentPreference, StudentMultiChoiceAnswer, StudentTheoryAnswer,
    Solution,
)
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils import timezone


class AssessmentPreferenceCreateForm(forms.ModelForm):
    class Meta:
        model = AssessmentPreference
        fields = ("duration", "due_date", "is_question_shuffle")

        widgets = {
            "due_date": forms.SplitDateTimeWidget(date_attrs={"type": "date", "class": "form-control", "title":"Date"},
                                                  time_attrs={"type": "time", "class": "form-control", "title":"Time"}),
            "duration": forms.TimeInput(attrs={"type": "time", "step": 1}),
        }
        field_classes = {
            "due_date": forms.SplitDateTimeField
        }

    def clean_due_date(self):
        due_date = self.cleaned_data.get("due_date")
        if due_date:
            if due_date < timezone.now():
                raise forms.ValidationError("Due Date can not be in the Past")
            elif due_date == timezone.now():
                raise forms.ValidationError("Dead line time should be at least 10 minute more than now")

        return due_date

    def clean_duration(self):
        duration = self.cleaned_data.get("duration")
        if duration and duration < timezone.timedelta(minutes=5):
                raise forms.ValidationError("Minimum duration should be 5 minutes. You provided %s " % duration)

        return duration


class MultiChoiceQuestionCreateForm(forms.ModelForm):
    class Meta:
        model = MultiChoiceQuestion
        fields = ("option", "is_answer_option",)
        widgets = {
            "option": forms.Textarea(attrs={"rows": 0}),
        }


class QuestionCreateForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ('group', 'question_number')


class QuestionGroupCreateForm(forms.ModelForm):
    class Meta:
        model = QuestionGroup
        fields = ("title", "questions_type", "course", "total_marks", "is_share_total_marks")
        labels = {
            "title": "Select Assessment title",
            "questions_type": "Assessment Type"
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                "unique_together": "This course has a quiz with this title already."
            }
        }


class QuestionGroupUpdateForm(forms.ModelForm):
    class Meta:
        model = QuestionGroup
        fields = ("title", "questions_type", "total_marks", "is_share_total_marks")
        labels = {
            "title": "Select Assessment title",
            "questions_type": "Assessment Type"
        }
        widgets = {
            "questions_type": forms.Select(attrs={"class": "no-pointer"})
        }
        error_messages = {
            NON_FIELD_ERRORS: {
                "unique_together": "This course has a quiz with this title already. Please change the title"
            }
        }

    def clean_title(self):
        title = self.cleaned_data.get("title")
        try:
            quiz = QuestionGroup.objects.get(title=title, course=self.instance.course)
        except QuestionGroup.DoesNotExist as err:
            return title
        else:
            last = title[-1]
            try:
                new_title = title[:len(title) - 1] + str( int(last) + 1)
            except TypeError as err:
                print(err)
                new_title = ""
            if self.instance.title == title:
                return title
            raise forms.ValidationError(f"{str(quiz.course)} already has ({quiz.get_title_display()}) assessment. Please try {new_title}.")

    def clean_questions_type(self):
        return self.initial["questions_type"]


def clean(self):
    """ Checks that no two or more optional is checked as correct answer in the same question."""

    if any(self.errors):
        # no other verification if the form contains error
        return
    correct_options = []
    for form in self.forms:
        try:
            if self.can_delete and self._should_delete_form(form):
                continue
        except AttributeError:
            continue
        option = form.cleaned_data.get('is_answer_option')
        if option in correct_options:
            raise forms.ValidationError(f"This question has more than {correct_options.__len__()} options marked as correct "
                                        f"answer. Please correct that, it must be only 1 correct answer for each "
                                        f"question.")
        if option:
            correct_options.append(option)
    if len(correct_options) == 0:
        raise forms.ValidationError("This question has no option marked as answer")


class BaseOptionsFormSet(forms.BaseFormSet):
    def clean(self):
        """ Checks that no two or more optional is checked as correct answer in the same question."""
        clean(self=self)


class BaseOptionsInlineFormSet(forms.BaseInlineFormSet):

    def clean(self):
        """ Checks that no two or more optional is checked as correct answer in the same question."""
        clean(self=self)


class StudentMultiChoiceAnswerForm(forms.ModelForm):
    class Meta:
        model = StudentMultiChoiceAnswer
        fields = ("selected_option", )
        labels = {
            "selected_option": "Select Any Option."
        }

        widgets = {
            "selected_option": forms.RadioSelect(attrs={"onclick": "handleChange()"}),
        }

    def __init__(self, question_instance, *args, **kwargs):
        super(StudentMultiChoiceAnswerForm, self).__init__(*args, **kwargs)
        self.fields["selected_option"].queryset = question_instance.multichoicequestion_set.all()


class StudentTheoryAnswerUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentTheoryAnswer
        fields = ("answer", )


class LectureQuestionSolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ("answer", "notes")
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 0})
        }
