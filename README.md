To replicate the results present in the screenshots, please follow the following steps:

NOTE: The steps work at the time of testing (23 September, 2023)

First create a python environment and install the packages from requirements.txt in the root directory of the repository.

```
pip install -r requirements.txt
```

I used miniconda to create an environment called "firm" where I installed all the required python libraries.
Please note that Python 3.10 was used.

```
conda create -n firm python=3.10 pip
conda activate firm
pip install -r requirements.txt
```

After it is installed, install minikube, istioctl and kubetnetes using your package manager for your respective operating system.

Also set up docker with networking parameter for minikube. The testing for this repository was done with network option:

```
export NO_PROXY=localhost,127.0.0.1,10.96.0.0/12,192.168.59.0/24,192.168.49.0/24,192.168.39.0/24
```

This concludes the initial prerequisites.

The next section is setup of kubernetes pods for tracing, observability and monitoring for the latency measurements.

NOTE: PLease run the command in the root directory of the repository unless specified.

1. Initialize minikube cluster

```
minikube start --mount --mount-string='/path/to/repo/user/:/path/to/repo/user' --memory=7000
```

2. Initialize istio

```
istioctl install
```

3. Install the strimzi system pod in default namespace

```
kubectl apply -f https://strimzi.io/install/latest
```

4. Install the monitoring and observability services in pods.

```
export NAMESPACE='monitoring'
kubectl create -f manifests/setup
kubectl create namespace observability
kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/v1.28.0/deploy/crds/jaegertracing.io_jaegers_crd.yaml
kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/v1.28.0/deploy/service_account.yaml
kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/v1.28.0/deploy/role.yaml
kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/v1.28.0/deploy/role_binding.yaml
kubectl create -n observability -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/v1.28.0/deploy/operator.yaml
kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/v1.28.0/deploy/cluster_role.yaml
kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/v1.28.0/deploy/cluster_role_binding.yaml
kubectl create -f manifests/
```

5. Deploy the storageclass for storing the database for tracing agent in default namespace.

```
kubectl apply -f storageclass/local-path.yml
```

6. Change directory to tracing-grapher

```
cd tracing-grapher
```

7. Build and run the docker image using docker-compose. Also deploy the neo4j, jupyter and kafka components through the docker container in trace-grapher namespace

```
docker-compose run stack-builder
cd deploy-trace-grapher
make install-components
```

Open a new terminal instance and go to the main repository again. Make sure not to close this docker container.
One can also run the contaienr in detached mode to just use the same terminal instance.

To remove the agents deployed through the docker container, (for debugging), run:

```
make purge
```

8. Wait for a few minutes for all pods to start running. To check for each of the pods status run:

```
kubectl get pods --all-namespaces
```

7. While these pods are starting, change directory to anomaly-injector in the root directory of the repository and run the following:

```
cd anomaly-detector
make
cd sysbench
./autogen.sh
./configure
make -j
make install
```

There might be some errors during install. Please install the following libraries to fix them: TODO

8. Install intel-cmt-cat through the third-party directory in the root directory

```
cd third-party
cd intel-cmt-cat
make
make install
```

9. Install the deployment module:

```
cd scripts
make all
cd python-cat-mba
make env
```

This concludes the initial setup of observation, monitoring, tracing, deployment modules and the anomaly injector.

Next is setting up the benchmark DeathStarBench social-network to generate svm and rl datasets to train the model for slo violation localization and mitigation.
