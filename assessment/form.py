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
        fields = ("duration", "due_date", "environment", "is_question_shuffle")

        widgets = {
            "due_date": forms.SplitDateTimeWidget(date_attrs={"type": "date", "class": "form-control"},
                                                  time_attrs={"type": "time", "class": "form-control"}),
            "duration": forms.TimeInput(attrs={"type": "time"}),
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
        if duration:
            if timezone.timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second) < timezone.timedelta(minutes=5):
                raise forms.ValidationError("Minimum duration should be 5 minutes")

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
                "unique_together": "Course with this type of assessment already exists"
            }
        }


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
