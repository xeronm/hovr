from django.db import models
from django.db.models.fields import reverse_related
from django.utils.translation import ugettext_lazy as _

def weakentity_str_identity(obj, key_list):
    if isinstance(key_list, tuple):
        key_list = list(key_list)
    return ':'.join([str(getattr(obj, x)) for x in key_list if hasattr(obj, x)])

class ModelAuditDates(models.Model):
    date_created = models.DateTimeField(verbose_name=_('Date created'), auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(verbose_name=_('Date updated'), auto_now=True, editable=False)
    
    class Meta:
        get_latest_by = 'date_updated'
        abstract = True

class OneToOneParentMixin(object):

    @property 
    def descendant(self):
        descendant = None
        for field in self._meta.get_fields():
            if not isinstance(field, reverse_related.OneToOneRel):
                continue
            if hasattr(self, field.name):
                descendant = getattr(self, field.name)
                break
        return descendant

    def __str__(self):
        descendant = self.descendant
        if descendant:
            return descendant.__str__()
        else:
            return super().__str__()

class ObjectIdentityNameMixin(object):
    def __str__(self):
        return self.name

class ObjectIdentityCodeMixin(object):
    def __str__(self):
        return self.code

class ObjectIdentityWeakMixin(object):
    def __str__(self):
        return weakentity_str_identity(self, self._meta.unique_together[0])



"""
!!! Important Note 1. !!! Do not change kwargs defaults. It leads to error in deconstruct method.
"""
class DescrField(models.CharField):
    max_length = 1024

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = self.max_length
        kwargs['null'] = True
        kwargs['blank'] = True
        if kwargs.get('verbose_name') is None:
            kwargs['verbose_name'] =  _('Description')
        super().__init__(*args, **kwargs)

class EntityNameField(models.CharField):
    max_length = 80

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = self.max_length
        kwargs['unique'] = True
        kwargs['db_index'] = True
        if kwargs.get('verbose_name') is None:
            kwargs['verbose_name'] =  _('Name')
        super().__init__(*args, **kwargs)

class EntityCodeField(models.CharField):
    max_length = 40

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = self.max_length
        kwargs['unique'] = True
        kwargs['db_index'] = True
        if kwargs.get('verbose_name') is None:
            kwargs['verbose_name'] =  _('Code')
        super().__init__(*args, **kwargs)

class EntityWeakCodeField(models.CharField):
    max_length = 30

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = self.max_length
        if kwargs.get('verbose_name') is None:
            kwargs['verbose_name'] =  _('Code')
        super().__init__(*args, **kwargs)

class QuantityField(models.DecimalField):
    max_digits=8
    decimal_places=2

    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = self.max_digits
        kwargs['decimal_places'] = self.decimal_places
        super().__init__(*args, **kwargs)

class PercentField(models.DecimalField):
    max_digits=6
    decimal_places=2

    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = self.max_digits
        kwargs['decimal_places'] = self.decimal_places
        super().__init__(*args, **kwargs)
