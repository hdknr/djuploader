from django.dispatch import dispatcher

uploaded = dispatcher.Signal(providing_args=["instance", ])
