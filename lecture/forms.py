from .models import LectureModel
from django import forms
from assessment.models import StudentTheoryAnswer


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
