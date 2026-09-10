from apps.members.models import Member


def create_member(*, full_name, email):
    return Member.objects.create(full_name=full_name, email=email)
