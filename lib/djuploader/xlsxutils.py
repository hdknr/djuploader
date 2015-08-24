# -*- coding: utf-8 -*-
from openpyxl import load_workbook

EXCEL2007 = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


class XlsxReader(object):
    def __init__(self, filename=None, headers=None, sheet=0):
        '''
            :type header: dict or None
            :param haeder: if None, the first row is `header`
        '''
        self.filename = filename
        self.sheet = sheet
        self.headers = headers
        if self.filename:
            self.book = load_workbook(filename=self.filename)

    def row_values(self, row):
        return [cell.value for cell in row if cell]

    def __iter__(self):
        header = list(self.headers or [])
        line = 0
        for row in self.book.worksheets[self.sheet].rows:
            line += 1
            if line == 1 and len(header) == 0:
                header = self.row_values(row)
                continue
            values = self.row_values(row)
            rowdict = dict(zip(header, values))
            yield line, rowdict, []
