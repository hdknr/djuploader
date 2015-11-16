# -*- coding: utf-8 -*-
'''
- https://ja.wikipedia.org/wiki/ダッシュ_%28記号%29
- http://docs.python.jp/2/howto/unicode.html#python-2-x-unicode

'''
from django.conf import settings
from django.utils.encoding import force_unicode, force_text

import csv
import io
import StringIO
import traceback
import nkf


class CsvReader(object):
    MIMETYPE = 'text/csv'

    def __init__(
        self, iterable, dialect='excel', error_mode="strict", encoding=None,
        headers=None, *args, **kwargs
    ):
        if isinstance(iterable, io.StringIO):
            assert encoding
            self.encoding = encoding
            iterable = StringIO.StringIO(iterable.read().encode(encoding))
        else:
            # force utf8 with nkf module
            self.encoding = 'utf8'
            iterable = StringIO.StringIO(nkf.nkf('-w', iterable.read()))

        self.headers = headers
        self.reader = headers and \
            csv.reader(iterable, dialect=dialect, *args, **kwargs) or \
            csv.DictReader(iterable, dialect=dialect, *args, **kwargs)
        self.dialect = self.reader.dialect
        self.line_num = 1
        self.error_mode = error_mode

    def reset_state(self):
        self.errors = ''
        self.col = 0

    def __iter__(self):
        return self

    def decode(self, value):
        ''' value: str '''
        self.col = self.col + 1
        return force_unicode(
            value, encoding=self.encoding, errors=self.error_mode).strip()

    def next(self):
        self.reset_state()
        self.line_num = self.reader.line_num

        if self.line_num == 0:          # TODO: 0, 2, 3, 4...
            self.line_num = 1

        line = self.reader.next()
        try:
            if self.headers:
                cols = dict(
                    zip(self.headers, [self.decode(x) for x in line]))
            else:
                cols = dict([(self.decode(k), self.decode(v))
                             for k, v in line.items()])
        except:
            self.errors = traceback.format_exc()
            cols = {}

        return self.line_num, cols, self.errors


class CsvWriter(object):
    MIMETYPE = 'text/csv'

    def __init__(
        self, stream, dialect=None, encoding=None, errors="strict", **kwds
    ):

        self.writer = csv.writer(stream, dialect=dialect or csv.excel, **kwds)
        self.encoding = encoding or settings.DEFAULT_CHARSET
        self.errors = errors

    def writerow(self, row):

        def _convert(s):
            if s is None:
                return ''
            if isinstance(s, basestring):
                return u'{0}'.format(force_text(s)).encode(self.encoding)
            return s

        self.writer.writerow(map(lambda s: _convert(s), row))

    def close(self):
        pass
