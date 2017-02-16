# -*- coding: utf-8 -*-
from django.utils.encoding import force_text
from django.http import HttpResponse

import mimetypes

from csvutils import CsvReader, CsvWriter
from xlsxutils import XlsxReader, XlsxWriter, XlsxBaseReader

DEFAULT_MIMETYPE = 'text/csv'


def get_mimetype(path):
    return mimetypes.guess_type(path)[0] or DEFAULT_MIMETYPE


def create_reader(mimetype, path, headless=False, *args, **kwargs):
    if mimetype == CsvReader.MIMETYPE:
        return CsvReader(open(path, 'rU'), *args, **kwargs)

    if 'encoding' in kwargs:
        kwargs.pop('encoding')
    if headless:
        return XlsxBaseReader(open(path), *args, **kwargs)
    return XlsxReader(open(path), *args, **kwargs)


def create_writer(mimetype, *args, **kwargs):
    return {
        CsvWriter.MIMETYPE: CsvWriter,
        XlsxWriter.MIMETYPE: XlsxWriter,
    }[mimetype](*args, **kwargs)


class FileResponse(HttpResponse):
    def __init__(
        self, content='', filename=None,
        content_type='application/octet-stream', *args, **kwargs
    ):
        if filename:
            content_type = get_mimetype(filename)

        super(FileResponse, self).__init__(
            content, content_type=content_type, *args, **kwargs)

        if filename:
            self.set_filename(filename)

    def set_filename(self, filename):
        self['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            force_text(filename).encode('utf8'))

    def export(self, queryset, header=True,
               excludes=[], relates=[], *args, **kwargs):
        queryset.export(
            self, header=header,
            excludes=excludes, relates=relates, **kwargs)
        return self
