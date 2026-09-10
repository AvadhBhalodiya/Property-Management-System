from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.members.models import Member
from apps.members.services import create_member


class MemberSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=Member.objects.all(),
                lookup="iexact",
                message="A member with this email already exists.",
            )
        ]
    )

    class Meta:
        model = Member
        fields = ["id", "full_name", "email", "created_at"]

    def create(self, validated_data):
        return create_member(**validated_data)
