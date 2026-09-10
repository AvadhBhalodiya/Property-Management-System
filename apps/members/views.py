from rest_framework import generics

from apps.members.models import Member
from apps.members.serializers import MemberSerializer


class MemberListCreateView(generics.ListCreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    success_messages = {
        "GET": "Members fetched successfully",
        "POST": "Member created successfully",
    }
