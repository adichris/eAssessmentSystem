from django.db import models
from django.utils.translation import gettext_lazy as _
from string import ascii_letters, digits
from random import choice
from django.utils.text import slugify
from PIL import Image
from django.shortcuts import redirect
from django.http.response import HttpResponseForbidden


class LevelInclusiveForStudentIn(models.TextChoices):
    YEAR_1 = 'y1', _('Year 1')
    YEAR_2 = 'y2', _('Year 2')
    YEAR_3 = 'y3', _('Year 3')
    YEAR_4 = 'y4', _('Year 4')
    ALL = 'all', _('All')
    __empty__ = _('(Unknown)')


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


def unique_department_slug_gen(instance, new_slug=None):
    if new_slug:
        slug = new_slug
    else:
        slug = slugify(instance.name)
    klass = instance.__class__
    qs_exists = klass.objects.filter(slug=slug).exists()
    if qs_exists:
        slug = "{slug}-{random}".format(slug=slug, random=random_string_gen())
        return unique_slug_gen(instance, new_slug=slug)
    else:
        return slug


def unique_slug_course_short_name(instance, new_slug=None):
    klass = instance.__class__
    if new_slug:
        slug = new_slug
    else:
        slug = slugify(instance.short_name)
        if slug is None or slug.lower() == 'none':
            slug = slugify(instance.name)
        if klass.objects.filter(slug=slug).exists():
            slug = slugify(instance.name + " " + str(instance.department))

    qs_exists = klass.objects.filter(slug=slug).exists()
    if qs_exists:
        slug = "{slug}-{random}".format(slug=slug, random=random_string_gen())
        return unique_slug_gen(instance, new_slug=slug)
    else:
        return slug


def resize_image(image, to_size=(400, 400)):
    img = Image.open(image.path)
    if img.width > to_size[0] or img.height > to_size[1]:
        img.thumbnail(to_size)
        img.save(image.path)


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


