from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.users.urls")),
    path("", include("apps.properties.urls")),
    path("", include("apps.members.urls")),
    path("", include("apps.contracts.urls")),
]
