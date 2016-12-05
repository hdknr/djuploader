# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

import csvutils
import xlsxutils
# import traceback

_EXCEL = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'xlsx',
]
_CSV = ['text/csv', 'csv', ]


class UploadModelQuerySet(models.QuerySet):
    def get_for(self, model_class, parent):
        res, _x = self.get_or_create(
            content_type=self.model.contenttype(model_class),
            parent_content_type=parent and self.model.contenttype(parent),)
        return res


class UploadQuerySet(models.QuerySet):

    def field_verbose_name(self, model, field_name):
        return model._meta.get_field_by_name(field_name)[0].verbose_name

    def get_field(self, model, name):
        return model._meta.get_field_by_name(name)

    def get_names(self, excludes=[]):
        def _cache():
            self._names = dict(
                (field.name, field)
                for field in self.model._meta.fields
                if field.name not in excludes
            )
        return getattr(self, '_names', _cache())

    def get_related_model_fields(self, relates=[]):
        def _cache():
            self._related_model_fields = {}
            for m, f in [r.split('.') for r in relates]:
                self._related_model_fields[m] = \
                    self._related_model_fields.get(m, []) + [f]
        return getattr(self, '_related_model_fields', _cache())

    def header_row(self, excludes=[], relates=[]):
        def _cache():
            names = self.get_names(excludes=excludes)

            self._header_row = [
                field.verbose_name for name, field in names.items()]

            related_model_fields = self.get_related_model_fields(relates)
            for rfn, rcs in related_model_fields.items():
                self._header_row += [
                    u"{0}.{1}".format(
                        rfn, self.field_verbose_name(
                            names[rfn].related_model, i))
                    for i in rcs]

        return getattr(self, '_header_row', _cache())

    def data_row(self, instance):
        cols = [
            getattr(instance, name, None) or ''
            for name, field in self.get_names().items()]

        for rfn, rcs in self.get_related_model_fields().items():
            value = getattr(instance, rfn)
            cols += [value and getattr(value, i, None) or '' for i in rcs]
        return cols

    def export(self,
               stream, format="csv", header=True, excludes=[], relates=[],
               **kwargs):

        if format in _EXCEL:
            writer = xlsxutils.XlsxWriter(stream, **kwargs)
        else:
            writer = csvutils.CsvWriter(stream, **kwargs)

        if header:
            writer.writerow(
                self.header_row(excludes=excludes, relates=relates))

        for instance in self.all():
            cols = self.data_row(instance)
            writer.writerow(cols)

        writer.close()

    def upload_for(self, fileobj, model_class=None, parent=None, **kwargs):
        model_class = model_class or self.model.MODEL_CLASS
        if not model_class:
            raise Exception(_('No Model Class'))

        upload = self.model._meta.get_field(
            'upload').related_model.objects.get_for(model_class, parent)

        if parent:
            kwargs['parent_object_id'] = parent.id

        return self.create(upload=upload, file=fileobj, **kwargs)

    def instanciate(self, parent=None, **kwargs):
        from .models import UploadModel
        upload = UploadModel.objects.get_for(self.model.MODEL_CLASS, parent)
        if parent:
            kwargs['parent_object_id'] = parent.id
        return self.model(upload=upload, **kwargs)

    def filter_for(self, model_class, parent=None):
        from .models import BaseModel
        params = dict(
            upload__content_type=BaseModel.contenttype(model_class),
            upload__parent_content_type=parent and BaseModel.contenttype(parent),  # NOQA
        )
        if parent:
            params['parent_object_id'] = parent.id
        return self.filter(**params)


class UploaderQuerySet(models.QuerySet):

    def create_uploader(self, parent=None, **kwargs):
        from .models import UploadModel, UploadFile
        upload = UploadModel.objects.get_for(self.model, parent)
        if parent:
            kwargs['parent_object_id'] = parent.id
        return UploadFile(upload=upload, **kwargs)

    def upload(self, fileobj, parent=None, **kwargs):
        uploader = self.create_uploader(parent=parent, file=fileobj, **kwargs)
        uploader.save()
        return uploader
