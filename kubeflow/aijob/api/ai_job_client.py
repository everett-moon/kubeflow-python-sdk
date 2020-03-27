import multiprocessing
import time
import logging

from kubernetes import client, config

from kubeflow.aijob.constants import constants
from kubeflow.aijob.utils import utils

from .ai_job_watch import watch as aijob_watch

logging.basicConfig(format='%(message)s')
logging.getLogger().setLevel(logging.INFO)

class AIJobClient(object):

  def __init__(self, config_file=None, context=None,
               client_configuration=None, persist_config=True):
    """
    AIJob client constructor
    :param config_file: kubeconfig file, defaults to ~/.kube/config
    :param context: kubernetes context
    :param client_configuration: kubernetes configuration object
    :param persist_config:
    """
    if config_file or not utils.is_running_in_k8s():
      config.load_kube_config(
        config_file=config_file,
        context=context,
        client_configuration=client_configuration,
        persist_config=persist_config)
    else:
      config.load_incluster_config()

    self.custom_api = client.CustomObjectsApi()
    self.core_api = client.CoreV1Api()


  def create(self, aijob, namespace=None):
    """
    Create the AIJob
    :param aijob: aijob object
    :param namespace: defaults to current or default namespace
    :return: created aijob
    """

    if namespace is None:
      namespace = utils.set_aijob_namespace(aijob)

    try:
      outputs = self.custom_api.create_namespaced_custom_object(
        constants.AIJOB_GROUP,
        constants.AIJOB_VERSION,
        namespace,
        constants.AIJOB_PLURAL,
        aijob)
    except client.rest.ApiException as e:
      raise RuntimeError(
        "Exception when calling CustomObjectsApi->create_namespaced_custom_object:\
         %s\n" % e)

    return outputs

  def get(self, name=None, namespace=None, watch=False, timeout_seconds=600):
    """
    Get the aijob
    :param name: existing aijob name, if not defined, the get all aijobs in the namespace.
    :param namespace: defaults to current or default namespace
    :param watch: Watch the AIJob if `True`.
    :param timeout_seconds: How long to watch the job..
    :return: aijob
    """
    if namespace is None:
      namespace = utils.get_default_target_namespace()

    if name:
      if watch:
        aijob_watch(
          name=name,
          namespace=namespace,
          timeout_seconds=timeout_seconds)
      else:
        thread = self.custom_api.get_namespaced_custom_object(
          constants.AIJOB_GROUP,
          constants.AIJOB_VERSION,
          namespace,
          constants.AIJOB_PLURAL,
          name,
          async_req=True)

        aijob = None
        try:
          aijob = thread.get(constants.APISERVER_TIMEOUT)
        except multiprocessing.TimeoutError:
          raise RuntimeError("Timeout trying to get AIJob.")
        except client.rest.ApiException as e:
          raise RuntimeError(
            "Exception when calling CustomObjectsApi->get_namespaced_custom_object:\
            %s\n" % e)
        except Exception as e:
          raise RuntimeError(
            "There was a problem to get AIJob {0} in namespace {1}. Exception: \
            {2} ".format(name, namespace, e))
        return aijob
    else:
      if watch:
        aijob_watch(
            namespace=namespace,
            timeout_seconds=timeout_seconds)
      else:
        thread = self.custom_api.list_namespaced_custom_object(
          constants.AIJOB_GROUP,
          constants.AIJOB_VERSION,
          namespace,
          constants.AIJOB_PLURAL,
          async_req=True)

        aijobs = None
        try:
          aijobs = thread.get(constants.APISERVER_TIMEOUT)
        except multiprocessing.TimeoutError:
          raise RuntimeError("Timeout trying to get AIJob.")
        except client.rest.ApiException as e:
          raise RuntimeError(
            "Exception when calling CustomObjectsApi->list_namespaced_custom_object:\
            %s\n" % e)
        except Exception as e:
          raise RuntimeError(
            "There was a problem to list aijobs in namespace {0}. \
            Exception: {1} ".format(namespace, e))
        return aijobs


  def patch(self, name, aijob, namespace=None):
    """
    Patch existing aijob
    :param name: existing aijob name
    :param aijob: patched aijob
    :param namespace: defaults to current or default namespace
    :return: patched aijob
    """
    if namespace is None:
      namespace = utils.set_aijob_namespace(aijob)

    try:
      outputs = self.custom_api.patch_namespaced_custom_object(
        constants.AIJOB_GROUP,
        constants.AIJOB_VERSION,
        namespace,
        constants.AIJOB_PLURAL,
        name,
        aijob)
    except client.rest.ApiException as e:
      raise RuntimeError(
        "Exception when calling CustomObjectsApi->patch_namespaced_custom_object:\
         %s\n" % e)

    return outputs


  def delete(self, name, namespace=None):
    """
    Delete the aijob
    :param name: aijob name
    :param namespace: defaults to current or default namespace
    :return:
    """
    if namespace is None:
      namespace = utils.get_default_target_namespace()

    try:
      return self.custom_api.delete_namespaced_custom_object(
        constants.AIJOB_GROUP,
        constants.AIJOB_VERSION,
        namespace,
        constants.AIJOB_PLURAL,
        name,
        client.V1DeleteOptions())
    except client.rest.ApiException as e:
      raise RuntimeError(
        "Exception when calling CustomObjectsApi->delete_namespaced_custom_object:\
         %s\n" % e)


  def wait_for_job(self, name, #pylint: disable=inconsistent-return-statements
                   namespace=None,
                   timeout_seconds=600,
                   polling_interval=30,
                   watch=False,
                   status_callback=None):
    """Wait for the specified job to finish.

    :param name: Name of the aijob.
    :param namespace: defaults to current or default namespace.
    :param timeout_seconds: How long to wait for the job.
    :param polling_interval: How often to poll for the status of the job.
    :param watch: Watch the aijob if `True`.
    :param status_callback: (Optional): Callable. If supplied this callable is
           invoked after we poll the job. Callable takes a single argument which
           is the job.
    :return:
    """
    if namespace is None:
      namespace = utils.get_default_target_namespace()

    if watch:
      aijob_watch(
        name=name,
        namespace=namespace,
        timeout_seconds=timeout_seconds)
    else:
      return self.wait_for_condition(
        name,
        ["Succeeded", "Failed"],
        namespace=namespace,
        timeout_seconds=timeout_seconds,
        polling_interval=polling_interval,
        status_callback=status_callback)


  def wait_for_condition(self, name,
                         expected_condition,
                         namespace=None,
                         timeout_seconds=600,
                         polling_interval=30,
                         status_callback=None):
    """Waits until any of the specified conditions occur.

    :param name: Name of the job.
    :param expected_condition: A list of conditions. Function waits until any of the
           supplied conditions is reached.
    :param namespace: defaults to current or default namespace.
    :param timeout_seconds: How long to wait for the job.
    :param polling_interval: How often to poll for the status of the job.
    :param status_callback: (Optional): Callable. If supplied this callable is
           invoked after we poll the job. Callable takes a single argument which
           is the job.
    :return: Object aijob status
    """

    if namespace is None:
      namespace = utils.get_default_target_namespace()

    for _ in range(round(timeout_seconds/polling_interval)):

      aijob = None
      aijob = self.get(name, namespace=namespace)

      if aijob:
        if status_callback:
          status_callback(aijob)

        # If we poll the CRD quick enough status won't have been set yet.
        conditions = aijob.get("status", {}).get("conditions", [])
        # Conditions might have a value of None in status.
        conditions = conditions or []
        for c in conditions:
          if c.get("type", "") in expected_condition:
            return aijob

      time.sleep(polling_interval)

    raise RuntimeError(
      "Timeout waiting for aijob {0} in namespace {1} to enter one of the "
      "conditions {2}.".format(name, namespace, expected_condition), aijob)


  def get_job_status(self, name, namespace=None):
    """Returns aijob status, such as Running, Failed or Succeeded.

    :param name: The aijob name.
    :param namespace: defaults to current or default namespace.
    :return: Object aijob status
    """
    if namespace is None:
      namespace = utils.get_default_target_namespace()

    aijob = self.get(name, namespace=namespace)
    last_condition = aijob.get("status", {}).get("conditions", [])[-1]
    return last_condition.get("type", "")


  def is_job_running(self, name, namespace=None):
    """Returns true if the aijob running; false otherwise.

    :param name: The aijob name.
    :param namespace: defaults to current or default namespace.
    :return: True or False
    """
    aijob_status = self.get_job_status(name, namespace=namespace)
    return aijob_status.lower() == "running"


  def is_job_succeeded(self, name, namespace=None):
    """Returns true if the aijob succeeded; false otherwise.

    :param name: The aijob name.
    :param namespace: defaults to current or default namespace.
    :return: True or False
    """
    aijob_status = self.get_job_status(name, namespace=namespace)
    return aijob_status.lower() == "succeeded"


  def get_pod_names(self, name, namespace=None, master=False, #pylint: disable=inconsistent-return-statements
                    replica_type=None, replica_index=None):
    """
    Get pod names of aijob.
    :param name: aijob name
    :param namespace: defaults to current or default namespace.
    :param master: Only get pod with label 'job-role: master' pod if True.
    :param replica_type: User can specify one of 'worker, ps, chief' to only get one type pods.
           By default get all type pods.
    :param replica_index: User can specfy replica index to get one pod of aijob.
    :return: set: pods name
    """

    if namespace is None:
      namespace = utils.get_default_target_namespace()

    labels = utils.get_labels(name, master=master,
                              replica_type=replica_type,
                              replica_index=replica_index)

    try:
      resp = self.core_api.list_namespaced_pod(
        namespace, label_selector=utils.to_selector(labels))
    except client.rest.ApiException as e:
      raise RuntimeError(
        "Exception when calling CoreV1Api->read_namespaced_pod_log: %s\n" % e)

    pod_names = []
    for pod in resp.items:
      if pod.metadata and pod.metadata.name:
        pod_names.append(pod.metadata.name)

    if not pod_names:
      logging.warning("Not found Pods of the aijob %s with the labels %s.", name, labels)
    else:
      return set(pod_names)


  def get_logs(self, name, namespace=None, master=True,
               replica_type=None, replica_index=None,
               follow=False):
    """
    Get training logs of the aijob.
    By default only get the logs of Pod that has labels 'job-role: master'.
    :param name: aijob name
    :param namespace: defaults to current or default namespace.
    :param master: By default get pod with label 'job-role: master' pod if True.
                   If need to get more Pod Logs, set False.
    :param replica_type: User can specify one of 'worker, ps, chief' to only get one type pods.
           By default get all type pods.
    :param replica_index: User can specfy replica index to get one pod of aijob.
    :param follow: Follow the log stream of the pod. Defaults to false.
    :return: str: pods logs
    """

    if namespace is None:
      namespace = utils.get_default_target_namespace()

    pod_names = self.get_pod_names(name, namespace=namespace,
                                   master=master,
                                   replica_type=replica_type,
                                   replica_index=replica_index)

    if pod_names:
      for pod in pod_names:
        try:
          pod_logs = self.core_api.read_namespaced_pod_log(
            pod, namespace, follow=follow)
          logging.info("The logs of Pod %s:\n %s", pod, pod_logs)
        except client.rest.ApiException as e:
          raise RuntimeError(
            "Exception when calling CoreV1Api->read_namespaced_pod_log: %s\n" % e)
    else:
      raise RuntimeError("Not found Pods of the aijob {} "
                         "in namespace {}".format(name, namespace))
