

from django.conf import settings
from django.contrib import admin
from django.db import models
from django.db.models.fields import Field
from django.dispatch import Signal
from django.forms import ModelForm, PasswordInput

from hashlib import sha256
from base64 import b64encode, b64decode
from cryptography.fernet import Fernet


workflow_post_save = Signal(providing_args=["workflow"])

encrypted_field_fernet = Fernet(b64encode(sha256(settings.ENCRYPTED_FIELD_KEY.encode('utf-8')).digest()))


class EncryptedField(Field):
    '''
    EncryptedField is used to modify (encrypt/decrypt)
    a value between the application and database.
    '''


    def __init__(self, field_type=None, *args, **kwargs):
        ''' We pass the underlying field_type that we want to use 'field_type' '''
        self.field_type = field_type
        super().__init__(*args, **kwargs)
        self.fernet = encrypted_field_fernet



    def deconstruct(self):
        ''' We want to use the passed in 'field_type as' our own if it is set '''
        name, path, args, kwargs = super().deconstruct()
        if self.field_type is not None:
            kwargs['field_type'] = self.field_type
        return name, path, args, kwargs

    def get_internal_type(self):
        ''' Return the passed in 'field_type' as our own '''
        return self.field_type().get_internal_type()

    def get_prep_value(self, value):
        ''' Prepare the value to be stored in the db (encrypt) '''
        if not value:
            return super().get_prep_value(value)
        return super().get_prep_value(b64encode(self.fernet.encrypt(value.encode()))).decode('utf-8')

    def from_db_value(self, value, expression, connection, context):
        ''' Prepare the value for use in the application (decrypt) or return None '''
        if not value:
            return value

        return self.fernet.decrypt(b64decode(value)).decode('utf-8')


class Workflow(models.Model):
    enabled = models.BooleanField(default=False)
    name    = models.CharField(max_length=50,  blank=False, null=False)

    def __str__(self):
        return f"{self.name}"


class WorkflowParameters(models.Model):
    workflow = models.ForeignKey(Workflow, related_name='parameters', on_delete=models.CASCADE, blank=False, null=False)
    name     = models.CharField(max_length=50,  blank=False, null=False)
    value   =  EncryptedField(models.CharField, max_length=500, blank=True, null=True)


class WorkflowParametersInlineForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(WorkflowParametersInlineForm, self).__init__(*args, **kwargs)
        self.fields['value'].widget = PasswordInput(render_value=True)

    class Meta:
        model = WorkflowParameters
        fields = ['name','value']


class WorkflowParametersInline(admin.TabularInline):
    model = WorkflowParameters
    readonly_fields = ["name"]
    fields = ('name', 'value')
    max_num=0
    form = WorkflowParametersInlineForm

    def has_delete_permission(self, request, obj=None):
        return False


class WorkflowAdmin(admin.ModelAdmin):
    readonly_fields = ["name"]
    fields = ('name', 'enabled')
    inlines = [
        WorkflowParametersInline,
    ]

    # Want to send this after all saves are completed. So we hook into log_change
    # This is a bit of a hack. But also the best place to get the top level changed object(obj)
    # after everything has been saved.
    def log_change(self, request, obj, change_msg):
        super(WorkflowAdmin, self).log_change(request, obj, change_msg)
        workflow_post_save.send(sender=self.__class__, workflow=obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False
