from datetime import datetime
from enum import Enum
import json
import yaml


class BaseObjectSerializer(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, object):
            ex = obj._excludes if hasattr(obj, '_excludes') else {}
            vals = obj._customes.copy() if hasattr(obj, '_customs') else {}
            vals.update(getattr(obj, '__dict__', {}))
            return dict([(k, v) for k, v in vals.items()
                         if k not in ex and not k.startswith('_') and v])

        return super(BaseObjectSerializer, self).default(obj)

    @classmethod
    def to_json(cls, obj, *args, **kwargs):
        return json.dumps(obj, cls=cls, *args, **kwargs)

    @classmethod
    def to_yaml(cls, obj, *args, **kwargs):
        return yaml.safe_dump(json.loads(cls.to_json(obj, *args, **kwargs)))
