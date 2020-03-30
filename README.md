### Python AIJob SDK for kubeflow

Support four operators in kubeflow:
* tf-operator
* pytorch-operator
* mxnet-operator
* mpi-operator

#### Samples

```
from kubernetes import client,config
from kubeflow import aijob

namespace = aijob.utils.get_default_target_namespace()
container = client.V1Container(
    name="tensorflow",
        image="gcr.io/kubeflow-ci/tf-mnist-with-summaries:1.0",
        command=[
                "python",
                "/var/tf_mnist/mnist_with_summaries.py",
                "--log_dir=/train/logs", "--learning_rate=0.01",
                "--batch_size=150"
        ]
        )

worker = aijob.V1ReplicaSpec(
    replicas=2,
        restart_policy="OnFailure",
        template=client.V1PodTemplateSpec(
            spec=client.V1PodSpec(
                        containers=[container]
                )
            )
        )

chief = aijob.V1ReplicaSpec(
    replicas=1,
        restart_policy="OnFailure",
        template=client.V1PodTemplateSpec(
            spec=client.V1PodSpec(
                        containers=[container]
                )
            )
        )

ps = aijob.V1ReplicaSpec(
    replicas=1,
        restart_policy="OnFailure",
        template=client.V1PodTemplateSpec(
            spec=client.V1PodSpec(
                        containers=[container]
                )
            )
        )

tfjob = aijob.V1AIJob(
    api_version="kubeflow.org/v1",
        kind="TFJob",
            metadata=client.V1ObjectMeta(name="mnist",namespace=namespace),
            spec=aijob.V1AIJobSpec(
                    clean_pod_policy="None",
                    tf_replica_specs={"Worker": worker,
                    "Chief": chief,
                    "PS": ps}
                )
        )
```
