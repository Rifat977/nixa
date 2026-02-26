from copy import copy

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


_django_context_patched = False


def _patch_django_context_py314():
    """Fix BaseContext.__copy__ on Python 3.14+ (copy(super()) fails there)."""
    global _django_context_patched
    if _django_context_patched:
        return
    from django.template.context import BaseContext

    def __copy__(self):
        duplicate = BaseContext()
        duplicate.__class__ = self.__class__
        duplicate.__dict__ = copy(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = __copy__
    _django_context_patched = True


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = _('University Manage')

    def ready(self):
        _patch_django_context_py314() 