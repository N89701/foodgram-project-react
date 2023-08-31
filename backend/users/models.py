from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import validate_username


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    email = models.EmailField(
        unique=True,
        max_length=settings.LENGTH_LIMITS['user_email']
    )
    username = models.CharField(
        _('username'),
        max_length=settings.LENGTH_LIMITS['user_username'],
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer.'
            'Letters, digits and @/./+/-/_ only.'
        ),
        validators=[UnicodeUsernameValidator(), validate_username],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(
        _('first name'),
        max_length=settings.LENGTH_LIMITS['user_first_name']
    )
    last_name = models.CharField(
        _('last name'),
        max_length=settings.LENGTH_LIMITS['user_last_name']
    )
    password = models.CharField(
        _('password'),
        max_length=settings.LENGTH_LIMITS['user_password']
    )

    class Meta:
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follows'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'
    )

    class Meta:
        ordering = ('user', 'author')
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='self-follow attempt'
            ),
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='repeated follow attemtp'
            )
        ]
