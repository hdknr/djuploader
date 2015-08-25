# -*- coding: utf-8 -*-
'''

'''
from django.utils.encoding import force_text
from django.http import HttpResponse
from csvutils import CsvReader, CsvWriter
from xlsxutils import XlsxReader, XlsxWriter


def create_reader(mimetype, *args, **kwargs):
    return {
        CsvReader.MIMETYPE: CsvReader,
        XlsxReader.MIMETYPE: XlsxReader,
    }[mimetype](*args, **kwargs)


def create_writer(mimetype, *args, **kwargs):
    return {
        CsvWriter.MIMETYPE: CsvWriter,
        XlsxWriter.MIMETYPE: XlsxWriter,
    }[mimetype](*args, **kwargs)


class FileResponse(HttpResponse):
    def __init__(
        self, content='', mimetype=None, status=None,
        content_type='application/octet-stream',
        filename=None, *args, **kwargs
    ):
        super(FileResponse, self).__init__(
            content, mimetype, status, content_type)

        if filename:
            self.set_filename(filename)

    def set_filename(self, filename):
        self['Content-Disposition'] = 'attachment; filename="{0}"'.format(
            force_text(filename).encode('utf8'))
