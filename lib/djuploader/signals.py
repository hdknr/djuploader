import django.dispatch


uploaded = django.dispatch.Signal(providing_args=["upload", ])


def uploaded_signal(upload):
    uploaded_queue.delay(upload_id=upload.id)


try:
    from celery import shared_task

    @shared_task
    def uploaded_queue(upload_id):
        from models import UploadFile
        upload = UploadFile.objects.get(id=upload_id)
        sender = upload.content_type.model_class()
        uploaded.send(sender=sender, upload=upload)

    @shared_task
    def hello(msg):
        return "you say " + msg

except:
    pass
