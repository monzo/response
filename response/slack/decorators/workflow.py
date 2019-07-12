import logging
logger = logging.getLogger('__init__')

from django.db.models.signals import post_save
from django.db.utils import ProgrammingError, OperationalError
from django.dispatch import receiver

from response.slack.models import Workflow, WorkflowParameters, CommsChannel, workflow_post_save

RESPONSE_WORKFLOWS = {}


def register_workflow(name, *args, **kwargs):
    def _wrapper(workflow_class):
        workflow_object = workflow_class(*args, **kwargs)
        RESPONSE_WORKFLOWS[name] = workflow_object
        try:
            # Add/get workflow to db
            db_workflow, created = Workflow.objects.get_or_create(name=name)
            # Add parameters to database
            for wfp in workflow_object.configuration_values:
                WorkflowParameters.objects.get_or_create(name=wfp, workflow=db_workflow)
            if db_workflow.enabled:
                workflow_object.enable(db_workflow)
            else:
                workflow_object.disable(db_workflow)
            return db_workflow
        except (ProgrammingError, OperationalError) as ex:
            logger.warn(f'This will error before workflow migration has been completed (first run) \n{ex}')
    return _wrapper


@receiver(workflow_post_save,  dispatch_uid="update_workflow") # Update after admin changes
def update_workflow(sender, workflow, **kwargs):
    if workflow.enabled:
        RESPONSE_WORKFLOWS[workflow.name].enable(workflow)
    else:
        RESPONSE_WORKFLOWS[workflow.name].disable(workflow)


class WorkflowClass(object):
    configuration_values = []
    def enable(self, workflow: Workflow):
        pass

    def disable(self, workflow: Workflow):
        pass
