# -*- coding: utf-8 -*-

import os
import mimetypes
from . import (signals, utils)
import json
import traceback


class UploadModel(object):

    def get_parents(self):
        if self.parent_content_type:
            return self.parent_content_type.get_all_objects_for_this_type()


class UploadFile(object):

    def signal(self, *args, **kwargs):
        sig = getattr(self.model_class, self.signal_name,
                      signals.uploaded_signal)
        sig.send(sender=type(self), instance=self)

    @property
    def mimetype(self):
        return mimetypes.guess_type(self.file.path)[0]

    @property
    def model_class(self):
        return self.upload.content_type.model_class()

    @property
    def model_meta(self):
        return self.model_class._meta

    @property
    def basename(self):
        return self.file and os.path.basename(self.file.name) or ''

    @property
    def parent_object(self):
        if self.upload and self.upload.parent_content_type and \
                self.parent_object_id:
            return self.upload.get_parents().filter(
                id=self.parent_object_id).first()

    def open(self, headers=None, *args, **kwargs):
        return utils.create_reader(
            self.mimetype, self.file.path, headers=headers, *args, **kwargs)

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

    def on_except(self, row, rowdata):
        message = "\n-----\n".join([
            json.dumps(rowdata, ensure_ascii=False),
            traceback.format_exc()])
        self.add_error(row, message)

    @property
    def error_count(self):
        return self.uploadfileerror_set.count()
