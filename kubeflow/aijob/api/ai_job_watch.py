import retrying
from kubernetes import client
from kubernetes import watch as k8s_watch
from table_logger import TableLogger

from kubeflow.aijob.constants import constants
from kubeflow.aijob.utils import utils

tbl = TableLogger(
  columns='NAME,STATE,TIME',
  colwidth={'NAME': 30, 'STATE':20, 'TIME':30},
  border=False)

@retrying.retry(wait_fixed=1000, stop_max_attempt_number=20)
def watch(name=None, namespace=None, timeout_seconds=600):
  """Watch the created or patched InferenceService in the specified namespace"""

  if namespace is None:
    namespace = utils.get_default_target_namespace()

  stream = k8s_watch.Watch().stream(
    client.CustomObjectsApi().list_namespaced_custom_object,
    constants.AIJOB_GROUP,
    constants.AIJOB_VERSION,
    namespace,
    constants.AIJOB_PLURAL,
    timeout_seconds=timeout_seconds)

  for event in stream:
    aijob = event['object']
    aijob_name = aijob['metadata']['name']
    if name and name != aijob_name:
      continue
    else:
      status = ''
      update_time = ''
      last_condition = aijob.get('status', {}).get('conditions', [])[-1]
      status = last_condition.get('type', '')
      update_time = last_condition.get('lastTransitionTime', '')

      tbl(aijob_name, status, update_time)

      if name == aijob_name:
        if status == 'Succeeded' or status == 'Failed':
          break
