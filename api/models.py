import uuid
from datetime import datetime, timedelta

from django.db import models
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings

import jwt

from .utils import UUIDEncoder


class UserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        if not email or not password:
            raise ValueError('User must provide an email and password')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    email = models.EmailField(
        db_index=True,
        validators=[validators.validate_email],
        unique=True,
        blank=False
    )

    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ('username', )

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def token(self):
        return self._generate_jwt_token()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=30)

        token = jwt.encode({
            'id': self.uuid,
            'exp': int(dt.strftime('%s'))
        },
            settings.SECRET_KEY, algorithm='HS256',
            json_encoder=UUIDEncoder
        )

        return token.decode('utf-8')


class PlaceManager(models.Manager):

    def _create_place(self, user: User, **extra_fields):
        if not user:
            raise ValueError('User must be provided')

        place = self.model(
            user=user,
            **extra_fields,
        )
        place.save(using=self._db)

        return place

    def create_place_for_history(self, user: User, **extra_fields):
        return self._create_place(user, **extra_fields)

    def set_place_to_favourite(self, is_favourite):
        place = self.model(
            is_favourite=is_favourite,
        )

        place.save(using=self._db)
        return place


class DateManager(models.Manager):

    def _create_date(self, place):
        visit_date = self.model(
            place=place,
        )
        visit_date.save(using=self._db)

        return visit_date

    def create_date_for_history(self, place):
        return self._create_date(place)


class Place(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=False, default='Sample Place', unique=True)
    is_favourite = models.BooleanField(default=False)
    category = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = PlaceManager()


class VisitDate(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_visited = models.DateTimeField(auto_now_add=True)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)

    objects = DateManager()


