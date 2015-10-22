# -*- coding: utf-8 -*-
from django.db import models

import csvutils
import xlsxutils


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

        writer = {
            'csv': csvutils.CsvWriter,
            'xlsx': xlsxutils.XlsxWriter, }[format](stream, **kwargs)

        if header:
            writer.writerow(
                self.header_row(excludes=excludes, realtes=relates))

        for instance in self.all():
            cols = self.data_row(instance)
            writer.writerow(cols)

        writer.close()
