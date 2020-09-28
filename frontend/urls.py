from django.urls import path, re_path

from frontend import views

urlpatterns = [
    re_path(r"^alter/.*", views.index, name="alter"),
]
