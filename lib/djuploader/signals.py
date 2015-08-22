import django.dispatch


uploaded = django.dispatch.Signal(providing_args=["upload", ])
