# -*- coding: utf-8 -*-
from django.db import models

import csvutils
import xlsxutils


class UploadQuerySet(models.QuerySet):

    def field_verbose_name(self, model, field_name):
        return model._meta.get_field_by_name(field_name)[0].verbose_name

    def get_field(self, model, name):
        return model._meta.get_field_by_name(name)

    def export(self,
               stream, format="csv", header=True, excludes=[], relates=[],
               **kwargs):

        if format == 'csv':
            writer = csvutils.CsvWriter(stream, **kwargs)
        else:
            writer = xlsxutils.XlsxWriter(stream, **kwargs)

        names = dict(
            (field.name, field)
            for field in self.model._meta.fields
            if field.name not in excludes
        )

        related_models = {}
        for m, f in [r.split('.') for r in relates]:
            related_models[m] = related_models.get(m, []) + [f]

        if header:
            cols = [field.verbose_name for name, field in names.items()]

            for rfn, rcs in related_models.items():
                cols += [
                    u"{0}.{1}".format(
                        rfn, self.field_verbose_name(
                            names[rfn].related_model, i))
                    for i in rcs]

            writer.writerow(cols)

        for row in self.all():
            cols = [
                getattr(row, name, None) or ''
                for name, field in names.items() if name not in excludes]

            for rfn, rcs in related_models.items():
                value = getattr(row, rfn)
                cols += [value and getattr(value, i, None) or '' for i in rcs]

            writer.writerow(cols)

        writer.close()
