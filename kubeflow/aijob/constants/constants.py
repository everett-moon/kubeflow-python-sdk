import os

# TFJob K8S constants
AIJOB_GROUP = 'kubeflow.org'
AIJOB_VERSION = os.environ.get('AIJOB_VERSION', 'v1')
AIJOB_LOGLEVEL = os.environ.get('AIJOB_LOGLEVEL', 'INFO').upper()

# How long to wait in seconds for requests to the ApiServer
APISERVER_TIMEOUT = 120

#AIJob Labels Name
AIJOB_CONTROLLER_LABEL = 'controller-name'
AIJOB_GROUP_LABEL = 'group-name'
AIJOB_ROLE_LABEL = 'job-role'

constants_attributed = {
        'TFJob': {
            'JOB_PLURAL': 'tfjobs',
            'NAME_LABEL': 'tf-job-name',
            'TYPE_LABEL': 'tf-replica-type',
            'INDEX_LABEL': 'tf-replica-index'
            },
        'PytorchJob': {
            'JOB_PLURAL': 'pytorchjobs',
            'NAME_LABEL': 'pytorch-job-name',
            'TYPE_LABEL': 'pytorch-replica-type',
            'INDEX_LABEL': 'pytorch-replica-index'
            },
        'MXJob': {
            'JOB_PLURAL': 'mxnetjobs',
            'NAME_LABEL': 'mxnet-job-name',
            'TYPE_LABEL': 'mxnet-replica-type',
            'INDEX_LABEL': 'mxnet-replica-index'
            },
        'MPIJob': {
            'JOB_PLURAL': 'mpijobs',
            'NAME_LABEL': 'mpi-job-name',
            'TYPE_LABEL': 'mpi-replica-type',
            'INDEX_LABEL': 'mpi-replica-index'
            }
        }

ai_operators = {
        'TFJob': 'tf-operator',
        'PytorchJob': 'pytorch-operator',
        'MXJob': 'mxnet-operator',
        'MPIJob': 'mpi-operator'
        }
