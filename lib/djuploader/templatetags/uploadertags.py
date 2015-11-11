# -*- coding: utf-8 -*-
from django import template
from django.contrib.contenttypes.models import ContentType

from djuploader.models import UploadModel

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_upload_model(context, model, parent=None):
    content_type = ContentType.objects.get_for_model(model)
    parent_content_type = parent and ContentType.objects.get_for_model(parent)
    res, _ = UploadModel.objects.get_or_create(
        content_type=content_type, parent_content_type=parent_content_type)
    return res
