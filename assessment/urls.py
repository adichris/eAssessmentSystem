from django.urls import path
from .views import (AssessmentQuestionGroupDetailView, CreateMultipleChoiceQuestion, DeleteQuestionGroup,
                    QuestionGroupCreateView, CreateTheoryQuestion, EditTheoryQuestion,
                    DeleteQuestion, MultiChoiceQuestionEdit, AssessmentView,
                    ConductAssessment, AssessmentPreferenceCreateView,
                    ConductingAssessment, StudentAssessmentView, LectureStudentScriptTemplateView,
                    QuestionGroupUpdateView, GenerateQMarksRedirectQGroupRV, AssessmentPreferenceUpdateView,
                    StudentAssessingTemplateView, MultiChoiceQuestionsExaminationView, QuestionResultTemplateView,
                    QuestionsPreviewTemplateView, QuestionResultDetailTemplateView, TheoryQuestionsExaminationView,
                    TheoryQuestionAnswerView, TheoryScriptStatusTemplateView, StopAllWorkTemplateView,
                    AddOneMoreTheoryQuestion, StudentCompletedPublishedAssessmentView
                    )


app_name = "assessment"
urlpatterns = [
    path("all/", AssessmentView.as_view(), name="all"),
    path("prepareQuestion/<str:courseName>/<int:coursePK>/", QuestionGroupCreateView.as_view(), name="create_group"),
    path("updateQuestionGroup/<str:courseName>/<int:coursePK>/<str:title>/<int:pk>", QuestionGroupUpdateView.as_view(),
         name="update_group"),
    path("prepareTheory/<str:QGT>/<int:QGPK>/", CreateTheoryQuestion.as_view(), name="prepare_theory"),
    path("preparetheoryplusonemore/<int:question_group_pk>/<str:question_group_title>/<str:questions_type>/", AddOneMoreTheoryQuestion.as_view(), name="add1theory"),
    path("prepareMultichoiceQuestion/<str:QGT>/<int:QGPK>/", CreateMultipleChoiceQuestion.as_view(),
         name="prepare_MCQ"),
    path("questiongroupdetails_detail/<str:courseName>/<str:title>/<int:pk>/",
         AssessmentQuestionGroupDetailView.as_view(), name="question_grp_detail"),
    path("question/update_multichoice_question/<str:group_title>/<int:questionPK>/", MultiChoiceQuestionEdit.as_view(),
         name="update_mcq"),
    path("question/update_theory/<str:group_title>/<int:pk>/", EditTheoryQuestion.as_view(), name="update_theory"),
    path("question/delete/<str:coursePK>/<str:group_title>/<int:pk>/", DeleteQuestion.as_view(),
         name="delete_question"),
    path("question_group/delete/<str:courseName>/<int:coursePK>/<int:pk>/", DeleteQuestionGroup.as_view(),
         name="delete_question_group"),
    path("conduct/<str:question_group_title>/<int:question_group_pk>", ConductAssessment.as_view(), name="conduct"),
    path("preference/<str:question_group_title>/<str:question_group_pk>/", AssessmentPreferenceCreateView.as_view(),
         name="preference"),
    path("preference/<str:question_group_title>/<str:question_group_pk>/<str:environment>/<int:pk>/",
         AssessmentPreferenceUpdateView.as_view(), name="preference_update"),
    path("conducting_test/<str:course_name>/<int:question_group_pk>/<int:course_pk>/", ConductingAssessment.as_view(),
         name="conducting"),
    path("conducting_test/preview_question/<str:question_group_title>/<str:question_group_pk>/",
         QuestionsPreviewTemplateView.as_view(), name="pre_questions_conducting"),

    # Assessment URLS
    path("student/view/", StudentAssessmentView.as_view(), name="student"),
    path("student/view/<str:course_code>/<str:course_name>", StudentCompletedPublishedAssessmentView.as_view(), name="completed_published_assessment4student"),

    path("lecture/student/script/<int:course_id>/<int:question_group_id>/<int:student_id>/<str:questions_type>/",
         LectureStudentScriptTemplateView.as_view(), name="lecture_student_script"),
    path("generateMarks/<str:QGT>/<int:QGPK>/", GenerateQMarksRedirectQGroupRV.as_view(), name="generate_marks"),
    path("student/HALL/<str:QGT>/<int:QGPK>/", StudentAssessingTemplateView.as_view(), name="student_assessing"),

    # Exam
    path("scripts/multichoice/start/<str:course_code>/<str:QGT>/<int:QGPK>/",
         MultiChoiceQuestionsExaminationView.as_view(), name="MCQ_exam_start"),
    path("scripts/theory/start/<str:question_group_title>/<int:question_group_id>/<str:semester>/",
         TheoryQuestionsExaminationView.as_view(), name="theory_exam_start"),
    path("scripts/theory/answer/<str:question_group_title>/<int:question_group_id>/<int:script_pk>/<int:question_pk>/",
         TheoryQuestionAnswerView.as_view(), name="theory_exam_answer"),
    path("examiniation/theory/scripts/<int:script_pk>/", TheoryScriptStatusTemplateView.as_view(),
         name="theory_exam_status"),

    # STOP ALL WORK
    path("examiniation/<int:question_group_pk>/<int:course_id>/<str:question_group_title>/",
         StopAllWorkTemplateView.as_view(), name="exam_stop_all"),

    # Results
    path("scripts/result/summary/multi_choice/<int:student_id>/<int:course_id>/<int:question_group_id>/<int:script_pk>/"
         "<str:questions_type>/", QuestionResultTemplateView.as_view(), name="result"),
    path("scripts/result/details/<int:student_id>/<int:course_id>/<int:question_group_id>/<str:questions_type>/",
         QuestionResultDetailTemplateView.as_view(), name="result_detail"),

]
