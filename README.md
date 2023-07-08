# How to run locally

Prerequisites

- kind v0.16.0
- kubectl v1.25.2
- helm v3.10.0

## Jump into the `iac/local` folder

```shell
cd iac/local
```

## Create k8s cluster

```shell
kind create cluster --config cluster_config.yaml
```

## Install Metallb

Since version 0.13.0, MetalLB is configured via CRs and the original way of configuring it 
via a ConfigMap based configuration is not working anymore.

```shell
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.5/config/manifests/metallb-native.yaml
kubectl get pods -n metallb-system --watch
```

To complete layer2 configuration, we need to provide metallb a range of IP addresses it controls.
We want this range to be on the docker kind network.

```shell
docker network inspect -f '{{.IPAM.Config}}' kind
```

The output will contain a cidr such as 172.19.0.0/16.
We want our loadbalancer IP range to come from this subclass.
We can configure metallb, for instance, to use 172.19.255.200 to 172.19.255.250 
by creating the IPAddressPool and the related L2Advertisement.

Update `metallb.yaml` file with proper IP range and apply it.

```shell
kubectl apply -f metallb.yaml
```

## Install MongoDB

```shell
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install mongodb bitnami/mongodb --values mongodb/values.yaml
```

It is also required to create a database and a user.

```
use thalassa
db.createUser(
    {
        user: "thalassa",
        pwd: "thalassa",
        roles: [
            "readWrite",
        ],
    },
)
```

## Install Airflow

### [OPTIONAL] Local installation

```shell
AIRFLOW_VERSION=2.4.1   
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-no-providers-${PYTHON_VERSION}.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}" 
```

### Build custom Docker image

```shell
cd src/etl
docker build -f Dockerfile.airflow --tag thalassa/airflow:0.0.1 .
kind load docker-image thalassa/airflow:0.0.1
```

### Install helm chart

```shell
cd iac/local
helm repo add apache-airflow https://airflow.apache.org
helm repo update
helm install airflow apache-airflow/airflow --values airflow/values.yaml
```

## Create .env.local in the `src` folder

```dotenv
MONGODB_HOST=100.120.8.200
MONGODB_USERNAME=thalassa
MONGODB_PASSWORD=thalassa

TWITTER_API_KEY=<YOUR_TWITTER_API_KEY>
TWITTER_KEY_SECRET=<YOUR_TWITTER_KEY_SECRET>
TWITTER_BEARER_TOKEN=<YOUR_TWITTER_BEARER_TOKEN>

SPARK_MONGODB_READ_URL=mongodb://thalassa:thalassa@100.120.8.200/thalassa
SPARK_MONGODB_WRITE_URL=mongodb://thalassa:thalassa@100.120.8.200/thalassa
```

## Install dependencies

```shell
poetry install
```

## Stream tweets

```shell
make consume-tweets
```

**Recently Twitter made it impossible to stream tweets without a paid subscription**

As an alternative, I recommend to download this data set: 
[Covid Tweets from Kaggle.](https://www.kaggle.com/datasets/gpreda/covid19-tweets)

Then, you should put the CSV into `src` folder and run a spark job to inject data into the DB.

```shell
make import-tweets-from-csv
```

## Preprocess tweets using spark

### If you streamed tweets yourself

```shell
make join-tweets-with-users
make clean-tweets
```

### If you downloaded tweets from Kaggle

```shell
make clean-tweets
```

## Count words using spark

```shell
make count-words
```

## Install Spark K8S Operator

### Install operator from the helm chart

```shell
helm repo add spark-operator https://googlecloudplatform.github.io/spark-on-k8s-operator
helm repo update
helm install spark-operator spark-operator/spark-operator --set image.tag=v1beta2-1.3.3-3.1.1 --namespace spark-operator --create-namespace
```

### Build image with spark jobs

```shell
cd src/etl
docker build -f Dockerfile.spark --tag thalassa/spark:0.0.1 .
kind load docker-image thalassa/spark:0.0.1
```

### Create namespace for spark applications

```shell
kubectl create namespace spark-applications
```

### Create service account (which will be used to run spark jobs) & role binding for it

```shell
cd iac/spark
kubectl apply -f service_account.yaml
kubectl apply -f role.yaml
kubectl apply -f role_binding.yaml
```

### Apply count_words job manually

```shell
kubectl apply -f jobs/count_words
```
