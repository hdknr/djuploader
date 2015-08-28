from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from djuploader.queryset import UploadQuerySet


class Profile(models.Model):
    GENDER_NA = 0
    GENDER_FEMALE = 1
    GENDER_MALE = 2

    user = models.ForeignKey(
        User, verbose_name=_('System User'))

    family_name = models.CharField(
        _('Family Name'), max_length=20)

    first_name = models.CharField(
        _('First Name'), max_length=20)

    birth_year = models.IntegerField(
        _('Birth Year'), null=True, blank=True, default=None)

    birth_month = models.IntegerField(
        _('Birth Month'), null=True, blank=True, default=None)

    birth_day = models.IntegerField(
        _('Birth Day'), null=True, blank=True, default=None)

    gender = models.IntegerField(
        _('Gender'), choices=(
            (GENDER_NA, _('Gender N/A'),),
            (GENDER_FEMALE, _('Gender Female'),),
            (GENDER_MALE, _('Gender Male'),),), default=GENDER_NA)

    created_at = models.DateTimeField(_(u'Created Datetime'), auto_now_add=True)
    updated_at = models.DateTimeField(_(u'Updated Datetime'), auto_now=True)

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profile')

    objects = models.Manager()              # default Manager
    uploader = UploadQuerySet.as_manager()
