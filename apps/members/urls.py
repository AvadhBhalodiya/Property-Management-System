from django.urls import path

from apps.members.views import MemberListCreateView

app_name = "members"

urlpatterns = [
    path("members", MemberListCreateView.as_view(), name="member-list"),
]
