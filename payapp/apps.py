from django.apps import AppConfig


class PayappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "payapp"

    def ready(self):
        from subprocess import Popen
        Popen(["python3", "thrift/TimestampServer/timestampserver.py"])
