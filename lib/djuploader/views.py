# -*- coding: utf-8 -*-
from django.http import Http404
from django.contrib.admin.views.decorators import staff_member_required

import models
import utils

import logging
logger = logging.getLogger('djuploader')
# import traceback


@staff_member_required
def download(request, path):
    upload = models.UploadFile.objects.filter(file=path).first()
    try:
        return utils.FileResponse(
            upload.file, content_type=upload.mimetype,
            filename=upload.basename)

    except:
        raise Http404
