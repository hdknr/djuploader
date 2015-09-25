from django.dispatch import dispatcher

uploaded_signal = dispatcher.Signal(providing_args=["instance", ])
