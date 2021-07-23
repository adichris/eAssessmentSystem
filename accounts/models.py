from django.core.checks import messages
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager as DefaultUserManager
from phonenumber_field.modelfields import PhoneNumberField
from eAssessmentSystem import tool_utils
from django.dispatch import receiver


class UserManager(DefaultUserManager):
    def create_user(self, first_name, last_name, username, phone_number, dob=None, password=None, **kwargs):
        """
        Creates and saves a User with the given username, phone number and password. and return the user object created
        """
        if not phone_number:
            raise ValueError('User must have phone number')

        user = self.model(
            phone_number=phone_number,
            username=username,
            first_name=first_name,
            last_name=last_name,
            dob=dob
        )

        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staff(self, first_name, last_name, username, phone_number, password, **kwargs):
        """
        Creates and saves a User(staff) with the given username, phone number and password.
        """
        if not phone_number:
            raise ValueError('User(staff) must have phone number')

        user = self.model(
            phone_number=phone_number,
            username=username,
            first_name=first_name,
            last_name=last_name
        )

        user.set_password(password)
        user.is_lecture = True
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, phone_number, password, **other_field):
        """
        Creates and saves a User(superuser) with the given username, phone number and password.
        """
        if not phone_number:
            raise ValueError('User(superuser) must have phone number')

        user = self.model(
            phone_number=phone_number,
            username=username,
            last_name=last_name,
            first_name=first_name
        )

        user.set_password(password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
    def get_staffs(self):
        return self.filter(
            is_admin=True,
            is_active=True,
            is_lecture=False
        )


class User(AbstractBaseUser):
    """Model definition for User."""
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=250)
    phone_number = PhoneNumberField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    dob = models.DateField(verbose_name="Date of Birth", null=True, blank=True)
    email = models.EmailField(verbose_name="Email Address", unique=True, null=True)
    slug = models.SlugField(null=True, blank=True, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_lecture = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']
    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"

    objects = UserManager()

    class Meta:
        """Meta definition for User."""
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        unique_together = ("first_name", "last_name", "dob")
        ordering = ("last_name", "first_name", "username")

    def __str__(self):
        """Unicode representation of User."""
        return self.get_full_name()

    def get_full_name(self):
        try:
            if self.generalsetting.name_order == "l":
                return "%s %s" % (self.last_name.title(), self.first_name.title())
            else:
                return "%s %s" % (self.first_name.title(), self.last_name.title())
        except AttributeError:
            return "%s %s" % (self.last_name.title(), self.first_name.title())

    def get_short_name(self):
        try:
            if self.generalsetting.name_order == "f":
                return self.first_name
            else:
                return self.last_name.title()
        except AttributeError:
            return self.first_name

    def get_name_abr(self):
        try:
            f_abr = "".join([list(n)[0] for n in self.first_name.split(" ")]).upper()
            l_abr = "".join([list(n)[0] for n in self.last_name.split(" ")]).upper()
           
            if self.generalsetting.name_order == "f":
                return f_abr+l_abr
            else:
                return l_abr+f_abr
        except AttributeError:
            return self.first_name

    def get_absolute_url(self):
        """Return absolute url for User."""
        from django.urls import reverse
        return reverse("accounts:user-profile", args=(self.slug, self.pk))

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        if self.is_superuser and self.is_admin:
            return True
        else:
            try:
                return super(User, self).has_perm(perm, obj)
            except AttributeError as e:
                pass

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        if self.is_admin:
            return True
        if self.is_staff:
            return True
    @property
    def is_staff(self):
        return (self.is_superuser or self.is_admin) and self.is_active


@receiver(models.signals.pre_save, sender=User)
def auto_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = tool_utils.unique_slug_gen(instance)