from django.urls import path
from .views import (AssessmentQuestionGroupDetailView, CreateMultipleChoiceQuestion, DeleteQuestionGroup,
                    QuestionGroupCreateView, CreateTheoryQuestion, EditTheoryQuestion,
                    DeleteQuestion, MultiChoiceQuestionEdit, AssessmentView,
                    ConductAssessment, MarkAssessment, AssessmentPreferenceCreateView,
                    ConductingAssessment, StudentAssessmentView, StudentResultTemplateView,
                    QuestionGroupUpdateView, GenerateQMarksRedirectQGroupRV, AssessmentPreferenceUpdateView,
                    StudentAssessingTemplateView, MultiChoiceQuestionsExaminationView, MultiChoiceQuestionResultTemplateView,
                    QuestionsPreviewTemplateView, MultiChoiceQuestionResultDetailTemplateView,
                    )


app_name = "assessment"
urlpatterns = [
    path("all/", AssessmentView.as_view(), name="all"),
    path("prepareQuestion/<str:courseName>/<int:coursePK>/", QuestionGroupCreateView.as_view(), name="create_group"),
    path("updateQuestionGroup/<str:courseName>/<int:coursePK>/<str:title>/<int:pk>", QuestionGroupUpdateView.as_view(), name="update_group"),
    path("prepareTheory/<str:QGT>/<int:QGPK>/", CreateTheoryQuestion.as_view(), name="prepare_theory"),
    path("prepareMultichoiceQuestion/<str:QGT>/<int:QGPK>/", CreateMultipleChoiceQuestion.as_view(), name="prepare_MCQ"),
    path("questiongroupdetails_detail/<str:courseName>/<str:title>/<int:pk>/", AssessmentQuestionGroupDetailView.as_view(), name="question_grp_detail"),
    path("question/update_multichoice_question/<str:group_title>/<int:questionPK>/", MultiChoiceQuestionEdit.as_view(), name="update_mcq"),
    path("question/update_theory/<str:group_title>/<int:pk>/", EditTheoryQuestion.as_view(), name="update_theory"),
    path("question/delete/<str:coursePK>/<str:group_title>/<int:pk>/", DeleteQuestion.as_view(), name="delete_question"),
    path("question_group/delete/<str:courseName>/<int:coursePK>/<int:pk>/", DeleteQuestionGroup.as_view(), name="delete_question_group"),
    path("conduct/<str:question_group_title>/<int:question_group_pk>", ConductAssessment.as_view(), name="conduct"),
    path("mark/", MarkAssessment.as_view(), name="mark"),
    path("preference/<str:question_group_title>/<str:question_group_pk>/", AssessmentPreferenceCreateView.as_view(), name="preference"),
    path("preference/<str:question_group_title>/<str:question_group_pk>/<str:environment>/<int:pk>/", AssessmentPreferenceUpdateView.as_view(), name="preference_update"),
    path("conducting_test/<str:course_name>/<int:question_group_pk>/<int:course_pk>/", ConductingAssessment.as_view(), name="conducting"),
    path("conducting_test/preview_question/<str:question_group_title>/<str:question_group_pk>/", QuestionsPreviewTemplateView.as_view(), name="pre_questions_conducting"),
    path("student/view/", StudentAssessmentView.as_view(), name="student"),
    path("student/result/", StudentResultTemplateView.as_view(), name="student_result"),
    path("generateMarks/<str:QGT>/<int:QGPK>/", GenerateQMarksRedirectQGroupRV.as_view(), name="generate_marks"),
    path("student/HALL/<str:QGT>/<int:QGPK>/", StudentAssessingTemplateView.as_view(), name="student_assessing"),

    path("examination/start/<str:course_code>/<str:QGT>/<int:QGPK>/", MultiChoiceQuestionsExaminationView.as_view(), name="MCQ_exam_start"),
    path("examination/result_detail.html/multi_choice/<int:student_id>/<int:course_id>/<int:question_group_id>/", MultiChoiceQuestionResultTemplateView.as_view(), name="result"),
    path("examination_done/multi_choice/<int:student_id>/<int:course_id>/<int:question_group_id>/", MultiChoiceQuestionResultDetailTemplateView.as_view(), name="result_detail"),

]
