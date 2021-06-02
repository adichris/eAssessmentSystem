from string import ascii_letters, digits
from random import choice
from django.utils.text import slugify
import datetime
from django.shortcuts import redirect
from django.http.response import HttpResponseForbidden


def random_string_gen(size=5, characters=ascii_letters + digits):
    return "".join(choice(characters) for _ in range(size))


def unique_slug_gen(instance, new_slug=None):
    if new_slug:
        slug = new_slug
    else:
        slug = slugify(instance.last_name + instance.first_name)
    klass = instance.__class__
    qs_exists = klass.objects.filter(slug=slug).exists()
    if qs_exists:
        slug = "{slug}-{random}".format(slug=slug, random=random_string_gen())
        return unique_slug_gen(instance, new_slug=slug)
    else:
        return slug


def admin_required_message(current_user):
    return f"""You are authenticated as <b>{current_user}</b>, but are not authorized to access this page. 
    Would you like to login to a different account?"""


def request_level_check(klass, klass_self, allow_lecture, is_post_request=False, *args, **kwargs):
    user = klass_self.request.user
    if user.is_active and (user.is_staff or (user.is_lecture and allow_lecture)):
        if is_post_request:
            return super(klass, klass_self).post(*args, **kwargs)
        else:
            return super(klass, klass_self).get(*args, **kwargs)
    else:
        klass_self.request.session["admin_required"] = admin_required_message(user)
        return redirect("accounts:staff-login-page")


def is_lecture(current_user):
    return current_user.is_lecture and current_user.is_active


def get_http_forbidden_response(message="Your not allowed to access this page because of your profile"):
    return HttpResponseForbidden(bytes(message, encoding="utf8", errors="ignore"))


def get_time_obj_from(timedelta):
    try:
        if not timedelta:
            return 0
        elif timedelta.days < 0:
            return -1
        elif timedelta:
            return datetime.time(hour=timedelta.seconds//3600,
                                 minute=(timedelta.seconds // 60) % 60,
                                 second=timedelta.seconds % 60
                                 )
    except AttributeError:
        return timedelta


