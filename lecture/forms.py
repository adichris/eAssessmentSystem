from .models import LectureModel
from django import forms
from assessment.models import StudentTheoryAnswer, QuestionTypeChoice, CourseModel


class LectureCreateForm(forms.ModelForm):
    class Meta:
        model = LectureModel
        fields = ("department", )


class StudentAnswerMarkForm(forms.ModelForm):

    class Meta:
        model = StudentTheoryAnswer
        fields = ("question", "answer", "score", "lecture_comment")
        widgets = {
            "question": forms.HiddenInput
        }
        labels = {
            "lecture_comment": "Leave a comment (optional)",
        }

    def __init__(self, *args, **kwargs):
        super(StudentAnswerMarkForm, self).__init__(*args, **kwargs)
        self.fields["answer"].widget.attrs["readonly"] = True
        self.fields["answer"].widget.attrs["class"] = "no-user-select"
        self.fields["lecture_comment"].widget.attrs["rows"] = "2"

    def clean_score(self):
        score = self.cleaned_data.get("score")
        question = self.cleaned_data.get("question")
        if score:
            if score > question.max_mark:
                raise forms.ValidationError("score mark(%s) given is greater than this question max score(%s)"
                                            % (score, question.max_mark))
            elif score < 0:
                score = 0
        return score


class FilterForms(forms.Form):
    marked = forms.CharField(widget=forms.CheckboxInput, required=False)
    marking = forms.CharField(widget=forms.CheckboxInput, required=False)
    submitted = forms.CharField(widget=forms.CheckboxInput, required=False, label="Unmarked")
    # pending = forms.CharField(widget=forms.CheckboxInput, required=False)


class QuestionGroupFilterForm(forms.Form):
    course = forms.ModelChoiceField(required=False, queryset=CourseModel.objects.all())
    assessment_type = forms.CharField(widget=forms.Select(choices=[(None, "---------")] + QuestionTypeChoice.choices ),
                                      required=False, initial=None)

    def __init__(self, course_queryset, *args, **kwargs):
        super(QuestionGroupFilterForm, self).__init__(*args, **kwargs)
        self.fields["course"].queryset = course_queryset.all()

