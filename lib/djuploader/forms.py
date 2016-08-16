# -*- coding: utf-8 -*-
from django import forms

from .models import UploadFile
from .queryset import UploaderQuerySet


class UploadForm(forms.ModelForm):

    class Meta:
        model = UploadFile
        exclude = [
            'upload', 'parent_object_id', 'user', 'status', 'name',
            'signal_name', ]

    @classmethod
    def instanciate(cls, data, files, model_class, parent=None, **kwargs):
        instance = UploaderQuerySet(model_class).create_uploader(parent=parent)
        return cls(data or None, files or None, instance=instance, **kwargs)
