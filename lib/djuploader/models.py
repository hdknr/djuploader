# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.fields.files import FieldFile
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
import mimetypes
import os
import signals
import csvutils
# import traceback


class BaseModel(models.Model):
    ordinal = models.IntegerField(
        _(u'Ordinal'), help_text=_(u'Ordinal Help'),
        default=0)
    created_at = models.DateTimeField(_(u'Created Datetime'), auto_now_add=True)
    updated_at = models.DateTimeField(_(u'Updated Datetime'), auto_now=True)

    class Meta:
        abstract = True

    def contenttype(self):
        return ContentType.objects.get_for_model(self.__class__)

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

    def get_internal_type(self):
        return 'FileField'

    def generate_filename(self, instance, filename):
        return u"{0}.{1}/{2}".format(
            instance.content_type.app_label,
            instance.content_type.model,
            filename,
        )

    def _storage(self, storage=None):
        if storage:
            return storage

        if self.DEFAULT_PREFIX:

            default_root = os.path.join(
                os.path.dirname(os.path.dirname(settings.MEDIA_ROOT)),
                '{0}/'.format(self.DEFAULT_PREFIX))
            default_url = '/{0}'.format(self.DEFAULT_PREFIX)

            location = self.MEDIA_ROOT and getattr(
                settings, self.MEDIA_ROOT, default_root) or default_root

            base_url = self.MEDIA_URL and getattr(
                settings, self.MEDIA_URL, default_url)

            storage = FileSystemStorage(
                location=location,
                base_url=base_url,)

            return storage

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


class UploadFile(BaseModel):
    content_type = models.ForeignKey(
        ContentType, verbose_name=_('Content Type'))

    name = models.CharField(
        _(u'Uploaded File Name'), max_length=200)
    file = UploadFileField(_('Uploaded File'))

    class Meta:
        verbose_name = _('Uploaded File')
        verbose_name_plural = _('Uploaded File')

    def signal(self):
        signals.uploaded.send(
            sender=self.content_type.model_class(),
            upload=self)

    @property
    def mimetype(self):
        return mimetypes.guess_type(self.file.path)[0]

    @property
    def model_meta(self):
        return self.content_type.model_class()._meta

    def open(self, headers=None):
        if self.mimetype == 'text/csv':
            return csvutils.UnicodeReader(
                self.file, headers=headers)

        # TODO: Excel and other file ...
        return []

    def get_fields_verbose(self):
        if not hasattr(self, '_fields_verbose'):
            self._fields_verbose = dict(
                (field.verbose_name, field)
                for field in self.model_meta.fields)
        return self._fields_verbose

    def get_field(self, name):
        ''' field name or verbose name '''
        meta = self.model_meta
        return name in meta.fields and meta.get_field_by_name(name) or \
            self.get_fields_verbose().get(name, None)

    def set_model_field_value(self, instance, field, value):
        try:
            if not (value == '' and field.null):
                value = field.to_python(value)
                setattr(instance, field.name, value)
        except ValidationError:
            pass

    def update_instance(self, instance, params, excludes=[]):
        for name, value in params.items():
            field = self.get_field(name)
            if field and field.name not in excludes:
                self.set_model_field_value(instance, field, value)
