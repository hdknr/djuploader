# -*- coding: utf-8 -*-
from django.http import Http404
from django.contrib.admin.views.decorators import staff_member_required

import models
import csvutils

import logging
logger = logging.getLogger('djuploader')
import traceback


@staff_member_required
def download(request, path):
    upload = models.UploadFile.objects.filter(file=path).first()
    try:
        if upload.mimetype == 'text/csv':
            return csvutils.CsvResponse(
                upload.file, filename=u"{0}.csv".format(upload.name))
    except:
        print traceback.format_exc()
        raise Http404
