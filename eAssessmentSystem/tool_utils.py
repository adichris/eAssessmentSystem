from string import ascii_letters, digits
from random import choice
from django.utils.text import slugify
import datetime
from django.shortcuts import redirect, render
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


def unique_slug_generator_scheme(klass, new_slug=None):
    """
    Generate a unique slug from
    :param instance:
    :param new_slug:
    :return:
    """
    if new_slug:
        slug = new_slug
    else:
        slug = slugify(random_string_gen(10))
    qs_exists = klass.objects.filter(slug=slug).exists()
    if qs_exists:
        slug = "{slug}-{random}".format(slug=slug, random=random_string_gen())
        return unique_slug_generator_scheme(klass, new_slug=slug)
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


def get_not_allowed_render_response(request, message="Your not allowed to access this page because of your profile"):
    return render(request, "assessment/status_not_allowed.html", {
        "reason": message
    })


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


def get_datetime_obj_from(timedelta):
    try:
        if not timedelta:
            return 0
        elif timedelta.days < 0:
            return -1
        elif timedelta:
            time = get_time_obj_from(timedelta)
            return datetime.datetime(0, 0, timedelta / datetime.timedelta(days=1), hour=time.hour, minute=time.minute, second=time.second)
    except AttributeError:
        return timedelta


def get_status_tips(question_group_instance, question_status):
    quiz_disallowed_edit = "The Quiz / Midsem is disallowed further editing."
    quiz_scheme_disallowed_edit = "The Quiz / Midsem and Marking Scheme is disallowed further editing."
    if question_group_instance.status == question_status.PREPARED:
        return "In preparing state only you can view, edit and delete the question"
    elif question_group_instance.status == question_status.CONDUCT:
        return "In conducting state student are accessing and doing the assessment. " + quiz_disallowed_edit

    elif question_group_instance.status == question_status.CONDUCTED:
        return "In conducted state the assessment has been taken and is ready for publish or marking. " +\
               quiz_disallowed_edit
    elif question_group_instance.status == question_status.PUBLISHED:
        return "In published state the assessment is conducted and student result and script is published." \
               "Student can review their script and see marking scheme if allowed to." \
               "Student can see correct multi-choice question answers. " + quiz_scheme_disallowed_edit

    elif question_group_instance.status == question_status.MARKED:
        return "In marked state student can see their score but can not review the scripts. " +\
               quiz_scheme_disallowed_edit


def general_setting_not_init(request):
    return render(
        request, "assessment/status_not_allowed.html",
        {
            "reason": "Please setup your semester and academic year to continue",
            "tip": "Goto general settings ⚙ and configure one. You only have to create it to much "
                   "your academic year and semester.",
            "settings_icon": True
        }
    )
