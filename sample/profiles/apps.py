from django.apps import AppConfig as DjangoAppConfig
from django.utils.translation import (
    ugettext_lazy as _,
)


class AppConfig(DjangoAppConfig):
    name = 'profiles'
    verbose_name = _("Profile")

    def ready(self):
        import signals
