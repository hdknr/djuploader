# -*- coding: utf-8 -*-
from django.utils.encoding import force_text
from django.http import HttpResponse

import mimetypes

from csvutils import CsvReader, CsvWriter
from xlsxutils import XlsxReader, XlsxWriter


def create_reader(mimetype, path, *args, **kwargs):
    if mimetype == CsvReader.MIMETYPE:
        return CsvReader(open(path, 'rU'), *args, **kwargs)

    XlsxReader(open(path), *args, **kwargs)


def create_writer(mimetype, *args, **kwargs):
    return {
        CsvWriter.MIMETYPE: CsvWriter,
        XlsxWriter.MIMETYPE: XlsxWriter,
    }[mimetype](*args, **kwargs)


class FileResponse(HttpResponse):
    def __init__(
        self, content='', filename=None,
        content_type='application/octet-stream',
        *args, **kwargs
    ):
        if filename:
            content_type = mimetypes.guess_type(filename)[0]

        super(FileResponse, self).__init__(
            content, content_type=content_type, *args, **kwargs)

        if filename:
            self.set_filename(filename)

    def set_filename(self, filename):
        self['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            force_text(filename).encode('utf8'))

    def export(self, model, header=True, *args, **kwargs):
        # objects implements UploadQuerySet
        model.objects.export(
            self, format=self.get('Content-Type', 'text/csv'),
            header=header, *args, **kwargs)
        return self
