# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.fields.files import FieldFile
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
import mimetypes
import os

# import traceback
from djasync.signals import async_receiver
import signals
import utils


class BaseModel(models.Model):
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
            instance.content_type.app_label,
            instance.content_type.model,
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


class UploadFile(BaseModel):
    parent_content_type = models.ForeignKey(
        ContentType, verbose_name=('Parent Content Type'),
        null=True, default=None, blank=True,)
    parent_object_id = models.PositiveIntegerField(
        null=True, default=None, blank=True,)

    parent = GenericForeignKey(
        'parent_content_type', 'parent_object_id', )

    content_type = models.ForeignKey(
        ContentType, verbose_name=_('Content Type'),
        related_name='target_content_type')

    name = models.CharField(
        _(u'Uploaded File Name'), max_length=200)
    file = UploadFileField(_('Uploaded File'))

    class Meta:
        verbose_name = _('Uploaded File')
        verbose_name_plural = _('Uploaded File')

    def __unicode__(self):
        return self.file.name

    @async_receiver
    def signal(self, *args, **kwargs):
        signals.uploaded.send(
            sender=self.content_type.model_class(),
            instance=self)

    @property
    def mimetype(self):
        return mimetypes.guess_type(self.file.path)[0]

    @property
    def model_meta(self):
        return self.content_type.model_class()._meta

    @property
    def basename(self):
        return self.file and os.path.basename(self.file.name) or ''

    def open(self, headers=None):
        return utils.create_reader(
            self.mimetype, self.file, headers=headers)

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

    def set_model_field_value(self, instance, row, field, value):
        try:
            if not value and field.null:
                # blank value
                return

            for v, l in field.choices:
                if value in (v, l):
                    value = v
                    break

            field.validate(value, instance)
            setattr(instance, field.name, field.to_python(value))

        except Exception, ex:
            self.add_error(
                row, _(u'Field Exception:{0}: "{1}" :{2}').format(
                    field.verbose_name, value, ex.message))

    def update_instance(self, instance, row, params, excludes=[]):
        '''
            :param row: data line number
        '''
        for name, value in params.items():
            field = self.get_field(name)
            if field and field.name not in excludes:
                self.set_model_field_value(instance, row, field, value)

    def clear(self):
        self.uploadfileerror_set.all().delete()

    def add_error(self, row, message):
        error, created = self.uploadfileerror_set.get_or_create(row=row)
        error.message += message + "\n"
        error.save()

    @property
    def error_count(self):
        return self.uploadfileerror_set.count()


class UploadFileError(BaseModel):
    upload = models.ForeignKey(UploadFile, verbose_name=_('Uploaded File'))
    row = models.IntegerField(_('Error Row'), help_text=_('Error Row Help'))
    message = models.TextField(_('Error Message'), default='')

    class Meta:
        verbose_name = _('Uploaded File Error')
        verbose_name_plural = _('Uploaded File Error')


def remove_missing_files():
    from django.utils._os import abspathu
    location = abspathu(UploadFileField.get_location())
    for (dirpath, dirnames, filenames) in os.walk(location):
        for name in filenames:
            fullpath = os.path.join(dirpath, name)
            if not UploadFile.objects.filter(
                    file=fullpath.replace(location + '/', '')).exists():
                os.remove(fullpath)
