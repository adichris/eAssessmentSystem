from django.urls import path
from .views import (RecordsView, StudentRecordTemplateView,
                    LectureRecordsTemplateView, LectureQuizRecordDetailView, PublishRecordsDetailView,
                    StudentRecordsTemplateView, LectureCourseRecords
                    )


app_name = "records"

urlpatterns = [
    path("all/", RecordsView.as_view(), name="all"),
    path("student/", StudentRecordTemplateView.as_view(), name="student"),
    path("lecture/all/", LectureRecordsTemplateView.as_view(), name="lecture_all"),
    path("lecture/course/<str:course_code>/<int:question_group_pk>/<str:question_group_title>/",
         LectureQuizRecordDetailView.as_view(), name="lecture_quiz_detail"),
    path("publish/<str:question_group_title>/<int:question_group_pk>/<str:course_code>/",
         PublishRecordsDetailView.as_view(), name="publish"),
    path("student/<str:course_code>/<int:course_id>", StudentRecordsTemplateView.as_view(), name="student_course_records"),
    path("lecture/course_detail/<int:course_pk>/<str:course_code>/", LectureCourseRecords.as_view(), name="course_detail"),
    path("adminlecturecourse_detail/<int:course_pk>/<str:course_code>/<int:lecture_id>/", LectureCourseRecords.as_view()
         , name="admin_view_lecture_course_detail"),
]

