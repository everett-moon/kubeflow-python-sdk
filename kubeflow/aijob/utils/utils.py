import os

from kubeflow.aijob.constants import constants

def is_running_in_k8s():
  return os.path.isdir('/var/run/secrets/kubernetes.io/')


def get_current_k8s_namespace():
  with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace', 'r') as f:
    return f.readline()


def get_default_target_namespace():
  if not is_running_in_k8s():
    return 'default'
  return get_current_k8s_namespace()


def set_aijob_namespace(job):
  job_namespace = job.metadata.namespace
  namespace = job_namespace or get_default_target_namespace()
  return namespace


def get_labels(name, kind, master=False, replica_type=None, replica_index=None):
  """
  Get labels according to speficed flags.
  :param name: aijob name
  :param kind: kind of this aijob, User can specify one of 'TFJob', 'PytorchJob', 'MXJob', 'MPIJob'
  :param master: if need include label 'job-role: master'.
  :param replica_type: User can specify one of 'worker, ps, chief to only' get one type pods.
  :param replica_index: Can specfy replica index to get one pod of AIJob.
  :return: Dict: Labels
  """
  labels = {
    constants.AIJOB_GROUP_LABEL: 'kubeflow.org',
    constants.AIJOB_CONTROLLER_LABEL: constants.ai_operators[kind],
    constants.AIJOB_NAME_LABEL[kind]: name,
  }

  if master:
    labels[constants.AIJOB_ROLE_LABEL] = 'master'

  if replica_type:
    labels[constants.AIJOB_TYPE_LABEL[kind]] = str.lower(replica_type)

  if replica_index:
    labels[constants.AIJOB_INDEX_LABEL[kind]] = replica_index

  return labels


def to_selector(labels):
  """
  Transfer Labels to selector.
  """
  parts = []
  for key in labels.keys():
    parts.append("{0}={1}".format(key, labels[key]))

  return ",".join(parts)
