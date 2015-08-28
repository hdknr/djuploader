# -*- coding: utf-8 -*-
from django.apps import AppConfig as DjangoAppConfig
from django.utils.translation import (
    ugettext_lazy as _,
)
from djasync.queue import CeleryLoader

celery = CeleryLoader(__file__)


class AppConfig(DjangoAppConfig):
    name = 'app'
    verbose_name = _("Application")

    def ready(self):
        self.celery = CeleryLoader.create()
