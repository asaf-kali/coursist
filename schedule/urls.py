from django.urls import path

from schedule.views import ScheduleView, SearchView, FetchClassesView

urlpatterns = [
    path("", ScheduleView.as_view(), name="schedule"),
    path("search", SearchView.as_view(), name="search_course"),
    path("fetch_classes", FetchClassesView.as_view(), name="fetch_classes"),
]
