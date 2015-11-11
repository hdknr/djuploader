# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# from django.utils.encoding import force_str
from djuploader.queryset import UploadQuerySet
from django.utils.translation import ugettext_lazy as _


class ContactQuerySet(UploadQuerySet):
    def header_row(self, excludes=[], relates=[]):
        ''' CSV Header '''
        return [_('Family Name'), _('First Name'), ]

    def data_row(self, instance):
        ''' CSV Data '''
        return [instance.family_name, instance.first_name, ]
