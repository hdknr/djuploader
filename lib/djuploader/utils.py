# -*- coding: utf-8 -*-
'''

'''
from django.utils.encoding import force_text
from django.http import HttpResponse


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
