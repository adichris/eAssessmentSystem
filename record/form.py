from django import forms
from course.models import CourseLevel
from assessment.models import QuestionGroupChoice
from programme.models import Programme


class LectureFilterForm(forms.Form):
    course = forms.ModelChoiceField(required=False, queryset=None)
    question_group_title = forms.CharField(label="Quiz", required=False, widget=forms.Select(choices=QuestionGroupChoice.choices))
    level = forms.ModelChoiceField(CourseLevel.objects.all(), required=False)
    programme = forms.ModelChoiceField(queryset=None, required=False)

    def __init__(self, lecture, *args, **kwargs):
        super(LectureFilterForm, self).__init__(*args, **kwargs)
        self.fields["course"].queryset = lecture.coursemodel_set.filter(semester=lecture.profile.generalsetting.semester)
        self.fields["programme"].queryset = Programme.objects.filter(coursemodel__lecture=lecture).distinct()