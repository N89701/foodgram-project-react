from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, F, Q
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    email = models.EmailField(unique=True, max_length=254)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    password = models.CharField(_('password'), max_length=150)

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
        constraints = [CheckConstraint(
            check=~Q(user=F('author')),
            name='self-follow attempt'
        )]
