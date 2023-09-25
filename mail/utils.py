from django.conf import settings
# Import Django-related code inside a function or method
from django.core.serializers.json import DjangoJSONEncoder
from .models import User

class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, User):
            return obj.id  # Or any other relevant user data
        return super().default(obj)

settings.JSON_ENCODER = 'mail.utils.CustomJSONEncoder'