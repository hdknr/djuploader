# -*- coding: utf-8 -*-
import types
import os
import sys
from kombu import Exchange, Queue
from celery import Celery


class CeleryLoader(types.ModuleType):
    ''' Celery
    ::

        $ celery -A app.queue.celery  worker -l info
    '''

    JOBQ = 'sandbox'
    CELERY = dict(
        CELERY_RESULT_BACKEND='amqp',
        CELERY_ACCEPT_CONTENT=['json'],
        CELERY_TASK_SERIALIZER='json',
        CELERY_RESULT_SERIALIZER='json',
        BROKER_URL='amqp://{0}:{1}@localhost:5672/{2}'.format(JOBQ, JOBQ, JOBQ),
        CELERY_DEFAULT_QUEUE=JOBQ,
        CELERY_QUEUES=(Queue(JOBQ, Exchange(JOBQ), routing_key=JOBQ),),
        # CELERY_ALWAYS_EAGER=True,
    )
    RABBITMQ = '''
sudo rabbitmqctl add_vhost {JOBQ}
sudo rabbitmqctl add_user {JOBQ} {JOBQ}
sudo rabbitmqctl set_permissions -p {JOBQ} {JOBQ} ".*" ".*" ".*"
'''.format(JOBQ=JOBQ)

    @classmethod
    def create(cls):
        from django.conf import settings
        celery = Celery('app')
        celery.config_from_object(cls.CELERY)
        celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
        return celery

    @property
    def app(self):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

        # bin/celery でsys.pathが変わるっぽい
        sys.path.insert(
            0,
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))))

        from django import apps, setup
        setup()
        return apps.apps.get_app_config('app').celery


celery = CeleryLoader('celery_loader')
