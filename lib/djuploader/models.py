# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.fields.files import FieldFile
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
import os
from django.contrib.auth import get_permission_codename


from . import methods, queryset


class BaseModel(models.Model):
    created_at = models.DateTimeField(_(u'Created Datetime'), auto_now_add=True)
    updated_at = models.DateTimeField(_(u'Updated Datetime'), auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def contenttype(cls, model=None):
        model = model or cls
        return ContentType.objects.get_for_model(model)

    def admin_change_url(self):
        url = 'admin:{0}_{1}_change'.format(
            self._meta.app_label, self._meta.model_name,
        )
        return reverse(url, args=[self.id])

    def admin_change_link(self, format=u'<a href="{0}">{1}</a>'):
        return mark_safe(format.format(
            self.admin_change_url(),
            self.__unicode__(),
        ))

    @classmethod
    def permission(cls, codename, model=None):
        model = model or cls
        return cls.contenttype(model).permission_set.filter(
            codename=codename).first()

    @classmethod
    def perm_name(cls, action, model=None):
        model = model or cls
        return "{}.{}".format(
            model._meta.app_label,
            get_permission_codename(action, model._meta))

    @classmethod
    def perm_code(cls, action, model=None):
        model = model or cls
        return get_permission_codename(action, model._meta)


class FieldFileEx(FieldFile):
    def move(self, new_name, save=True):
        original = self.file
        self.save(new_name, original, save=save)
        original.close()
        self.storage.delete(original.name)

    move.alters_data = True


class UploadFileField(models.FileField):
    attr_class = FieldFileEx

    MEDIA_ROOT = 'UPLOAD_MEDIA_ROOT'
    MEDIA_URL = 'UPLOAD_MEDIA_URL'
    DEFAULT_PREFIX = 'upload'

    @classmethod
    def get_location(cls):
        root = os.path.join(
            os.path.dirname(os.path.dirname(settings.MEDIA_ROOT)),
            '{0}/'.format(cls.DEFAULT_PREFIX))

        location = cls.MEDIA_ROOT and getattr(
            settings, cls.MEDIA_ROOT, root) or root

        return location

    @classmethod
    def get_base_url(cls):
        default_url = '/{0}'.format(cls.DEFAULT_PREFIX)
        base_url = cls.MEDIA_URL and getattr(
            settings, cls.MEDIA_URL, default_url)
        return base_url

    def get_internal_type(self):
        return 'FileField'

    def generate_filename(self, instance, filename):
        return u"{0}.{1}/{2}".format(
            instance.upload.content_type.app_label,
            instance.upload.content_type.model,
            filename,
        )

    def _storage(self, storage=None):
        if storage or not self.DEFAULT_PREFIX:
            return storage

        return FileSystemStorage(
            location=self.get_location(),
            base_url=self.get_base_url(),)

    def __init__(
        self, verbose_name=None, name=None,
        upload_to='', storage=None, **kwargs
    ):
        storage = self._storage(storage)

        super(UploadFileField, self).__init__(
            verbose_name=verbose_name, name=name,
            upload_to=upload_to, storage=storage, **kwargs)

    def is_valid_prefix(self, prefix):
        return True


class UploadModel(BaseModel, methods.UploadModel):
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_('Updating Model'), help_text=_('Updating Model Help'), )
    parent_content_type = models.ForeignKey(
        ContentType, related_name='uploadmodel_parent',
        verbose_name=_('Parent of Updating Model'),
        help_text=_('Parent of Updating Model Help'),
        null=True, default=None, blank=True,)

    class Meta:
        verbose_name = _('Upload Model')
        verbose_name_plural = _('Upload Model')

    def __unicode__(self):
        if self.parent_content_type:
            p = self.parent_content_type.__unicode__()
        else:
            p = ''

        return u"{0} {1}".format(p, self.content_type.__unicode__())

    objects = queryset.UploadModelQuerySet.as_manager()


class UploadFile(BaseModel, methods.UploadFile):
    MODEL_CLASS = None

    STATUS_UPLOADED = 0
    STATUS_PROCESSING = 10
    STATUS_COMPLETED = 20

    upload = models.ForeignKey(
        UploadModel,
        verbose_name=_('Updating Model'), help_text=_('Updating Model Help'),
        null=True, default=None, blank=True,)

    parent_object_id = models.PositiveIntegerField(
        verbose_name=_('Parent of Updating Model'),
        help_text=_('Parent of Updating Model Help'),
        null=True, default=None, blank=True,)

    name = models.CharField(
        _(u'Uploaded File Name'), max_length=200,
        null=True, default=None, blank=True,)

    file = UploadFileField(_('Uploaded File'))

    status = models.IntegerField(
        _('Upload File Status'),
        help_text=_('Upload File Status Help'),
        choices=(
            (STATUS_UPLOADED, _('File Uploaded'),),
            (STATUS_PROCESSING, _('File Under Processing'),),
            (STATUS_COMPLETED, _('File Process Completed'),),
        ), default=STATUS_UPLOADED)

    user = models.ForeignKey(
        User,
        verbose_name=_('Upload User'), help_text=_('Upload User Help'),
        null=True, default=None, blank=True,)

    signal_name = models.CharField(
        _(u'Signal Name'), help_text=_(u'Signal Name'),
        max_length=30, default="uploaded_signal")

    class Meta:
        verbose_name = _('Uploaded File')
        verbose_name_plural = _('Uploaded File')

    def __unicode__(self):
        return self.name or (self.file and self.file.name) or ''

    objects = queryset.UploadQuerySet.as_manager()


class UploadFileError(BaseModel):
    upload = models.ForeignKey(UploadFile, verbose_name=_('Uploaded File'))
    row = models.IntegerField(_('Error Row'), help_text=_('Error Row Help'))
    message = models.TextField(_('Error Message'), default='')
    exception = models.TextField(
        _('Error Exception'), default='', blank=True, null=True)

    class Meta:
        verbose_name = _('Uploaded File Error')
        verbose_name_plural = _('Uploaded File Error')

    def __unicode__(self):
        return u"{} {}".format(
            self.upload and self.upload.__unicode__() or '',
            self.row or '')


def remove_missing_files():
    from django.utils._os import abspathu
    location = abspathu(UploadFileField.get_location())
    for (dirpath, dirnames, filenames) in os.walk(location):
        for name in filenames:
            fullpath = os.path.join(dirpath, name)
            if not UploadFile.objects.filter(
                    file=fullpath.replace(location + '/', '')).exists():
                os.remove(fullpath)
