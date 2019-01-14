from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class InventoryConfig(AppConfig):
    name = 'dashboard.inventory'
    verbose_name = _('Inventory')