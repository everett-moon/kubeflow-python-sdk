import os

# TFJob K8S constants
AIJOB_GROUP = 'kubeflow.org'
AIJOB_KIND = 'AIJob'
AIJOB_PLURAL = 'aijobs'
AIJOB_VERSION = os.environ.get('AIJOB_VERSION', 'v1')
AIJOB_LOGLEVEL = os.environ.get('AIJOB_LOGLEVEL', 'INFO').upper()

# How long to wait in seconds for requests to the ApiServer
APISERVER_TIMEOUT = 120

#AIJob Labels Name
AIJOB_CONTROLLER_LABEL = 'controller-name'
AIJOB_GROUP_LABEL = 'group-name'
AIJOB_ROLE_LABEL = 'job-role'

AIJOB_TYPE_LABEL = {
        'TFJob': 'tf-replica-type',
        'PytorchJob': 'pytorch-replica-type',
        'MXJob': 'mxnet-replica-type',
        'MPIJob': 'mpi-replica-type'
        }
AIJOB_INDEX_LABEL = {
        'TFJob': 'tf-replica-index',
        'PytorchJob': 'pytorch-replica-index',
        'MXJob': 'mxnet-replica-index',
        'MPIJob': 'mpi-replica-index'
        }

AIJOB_NAME_LABEL = {
        'TFJob': 'tf-job-name',
        'PytorchJob': 'pytorch-job-name',
        'MXJob': 'mxnet-job-name',
        'MPIJob': 'mpi-job-name'
        }

ai_operators = {
        'TFJob': 'tf-operator',
        'PytorchJob': 'pytorch-operator',
        'MXJob': 'mxnet-operator',
        'MPIJob': 'mpi-operator'
        }
