from apps.users.models import User


def register_user(*, email, full_name, password):
    return User.objects.create_user(email=email, full_name=full_name, password=password)
