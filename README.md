This is a project aimed to demonstrate the basics of Kubernetes, Apache Kafka and Python. The goal is to build a simple application that fetches stock information from the Internet and then sends it to Kafka cluster to be processed a Kafka consumer. What you will see here is a very simplified setup — not what is usually implemented in production but a great way to understand the basics.

# Architecture

The application is composed of the following: a data extractor, a processor and the Kafka cluster. The data extractor (stock-data-fetcher) fetches the current stock data and sends it to Kafka which acts as a message broker. Then, the processor (stock-data-processor) receives the data and prints the information it received onto standard output. All these components are managed within a Kubernetes cluster.

# Installation Requirements

***Note: This project was developed to run on a Mac with M1 chip (ARM64 architecture). The instructions below are for this specific setup. If you are using a different architecture or operating system, you might need to make some changes to the instructions in this Readme file and possibly in the code as well. For example, you might need to change the base image in the Dockerfiles or Kubernetes configuration files to a different one that is compatible with your architecture. For Kakfa, I am using ARM64 images from the Confluent repository for both the Broker and the Zookeeper deployments.***

To run this project, you will need the following:
- `Minikube` - a tool that allows you to run a Kubernetes cluster on your local machine in a Docker container. You will not need to install Kubernetes, as Minikube will install it for you.
  - Recommended version: 1.27.0
- `Docker Desktop` - a tool that allows you to build and run containers.
  - Recommended version: 4.12.0

## Minikube

You can find the installation instructions for Minikube [here](https://minikube.sigs.k8s.io/docs/start/). Verify that Minikube is installed by running the following command `minikube version`.

```
% minikube version

minikube version: v1.27.0
commit: 4243041b7a72319b9be7842a7d34b6767bbdac2b
```

## Docker Desktop

You can find the installation instructions for Docker Desktop [here](https://docs.docker.com/get-docker/). Verify that Docker is installed by running the Docker Desktop application to start the Docker daemon. Once the Docker daemon is running, you can verify that Docker is installed by running the following command `docker version`.

```
% docker version

Client:
 Cloud integration: v1.0.29
 Version:           20.10.17
 API version:       1.41
 Go version:        go1.17.11
 Git commit:        100c701
 Built:             Mon Jun  6 23:04:45 2022
 OS/Arch:           darwin/arm64
 Context:           default
 Experimental:      true

Server: Docker Desktop 4.12.0 (85629)
 Engine:
  Version:          20.10.17
  API version:      1.41 (minimum version 1.12)
  Go version:       go1.17.11
  Git commit:       a89b842
  Built:            Mon Jun  6 23:01:01 2022
  OS/Arch:          linux/arm64
  Experimental:     false
 containerd:
  Version:          1.6.8
  GitCommit:        9cd3357b7fd7218e4aec3eae239db1f68a5a6ec6
 runc:
  Version:          1.1.4
  GitCommit:        v1.1.4-0-g5fd4c4d
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0
```

# Running the project

1. Start the Docker daemon by running the Docker Desktop application.
2. Start the Minikube cluster by running the following command `minikube start`. At first, this will take a while as it will download the Kubernetes images.
3. Verify that the Minikube cluster is running by running the following command `kubectl get nodes`.
4. Deploy the Kafka zookeeper by running the following command `kubectl apply -f kubernetes/zookeeper.yaml`.
5. Once the zookeeper is deployed, deploy the Kafka broker by running the following command `kubectl apply -f kubernetes/kafka-broker.yaml`.
6. Build the container image for the Stock Data Processor Python application by running the following command `docker build -t stock-data-processor -f apps/stock-data-processor/Dockerfile apps/stock-data-processor`.
9. Load the container image into the Minikube cluster by running the following command `minikube image load stock-data-processor`.
7. Deploy the Stock Data Processor application by running the following command `kubectl apply -f kubernetes/stock-data-processor.yaml`.
8. Build the container image for the Stock Data Fetcher Python application by running the following command `docker build -t stock-data-fetcher -f apps/stock-data-fetcher/Dockerfile apps/stock-data-fetcher`.
9. Load the container image into the Minikube cluster by running the following command `minikube image load stock-data-fetcher`.
10. Deploy the Stock Data Fetcher application as a Kubernetes resource by running the following command `kubectl apply -f kubernetes/stock-data-fetcher.yaml`. This is a Kubernetes cronjob that will run at a regular interval as defined in the cron expression to fetch the stock data for the predefined stocks.
11. To run the cronjob immediately, you can run the following command `kubectl create job --from=cronjob/stock-data-fetcher <job name>`.

# Monitoring and Logging

## View Kubernetes Resources

To view all the Kubernetes resources in the Minikube cluster, run the following command `kubectl get all`. You should see a list of all Kubernetes resources in the cluster - pods, services, deployments, cronjobs, jobs etc. You should see an output similar to the following:

```
% kubectl get all
NAME                                        READY   STATUS      RESTARTS        AGE
pod/fetch-01-v2529                          0/1     Completed   0               8d
pod/kafka-broker-6d8bc78b59-st68t           1/1     Running     1 (3m45s ago)   8d
pod/stock-data-processor-5566dc9688-j8z8h   1/1     Running     1 (8d ago)      8d
pod/zookeeper-646f758655-nprbk              1/1     Running     6 (8d ago)      11d

NAME                           TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)              AGE
service/kafka-broker-service   ClusterIP   10.105.158.79    <none>        29092/TCP,9092/TCP   8d
service/kubernetes             ClusterIP   10.96.0.1        <none>        443/TCP              11d
service/zookeeper-service      NodePort    10.108.208.103   <none>        2181:30181/TCP       11d
...
```

To view realtime updates to Kubernetes resources of a particular type, run the following command `kubectl get <resource-type> -w`. For example, to view realtime updates to the pods in the cluster, run the following command `kubectl get pods -w`.

## View Logs of Kubernetes Resources

To view the logs of a Kubernetes pod, run the following command `kubectl logs <pod-name>`. For example,

```
% kubectl logs pod/stock-data-processor-5566dc9688-j8z8h
Topic: stock-details
Server: kafka-broker-service:29092
Listening for stock updates ...
...
```

To view the logs of a Kubernetes job, run the following command `kubectl logs job/<job-name>`.

# Development and Testing

## Testing Kubernetes Resources

To develop and test the Kubernetes resources, just redeploy the Kubernetes resources by running the following command `kubectl apply -f kubernetes/<resource-name>.yaml`. Delete existing resources if necessary using `kubectl delete` command.

## Testing Python Applications

Python applications can be tested in Kubernetes by rebuilding the corresponding container image following the instructions above when deploying Kubernetes resources via `kubectl`.

To test locally, follow the instructions below:
1. Install Python (either via Homebrew or using a Python version manager like [pyenv](https://github.com/pyenv/pyenv)). Recommended Python version is defined in the `.python-version` file.
2. Create a Python virtual environment for your application. Each application should have its own virtual environment. The following [docs](https://docs.python.org/3/tutorial/venv.html) show how to create a virtual environment in Python. If you installed `pyenv`, you can use the `pyenv-virtualenv` plugin to easily manage your virtual environments.  For more information on pyenv-virtualenv, check https://github.com/pyenv/pyenv-virtualenv. The recommended Python version and virtual environment name is in `.python-version` file in the following format: `<python-version>/env/<virtual-environment-name>`. To create a virtual environment with pyenv-virtualenv, run the following command `pyenv virtualenv <python-version> <virtual-environment-name>`. For example, `pyenv virtualenv 3.10.7 stock-data-processor`.
3. If the application is connecting to Kafka, continue with step 4; otherwise, skip to step 6.
4. Run the Kubernetes cluster and make sure both Kafka zookeeper and broker are running
5. Expose the port of the Kafka broker by running the following command `kubectl port-forward service/kafka-broker-service 9093:9093`. This means that the Kafka broker will be accessible at `localhost:9093` and requests will be forwarded to port 9093 in the Minikube cluster.
6. Activate the virtual environment created in step 2.
7. Run `pip install -r requirements.txt` in the application directory to install the dependencies.
8. Set the environment variables required by the application as stated in the `local.env` file, if any. To set the environment variables, run the following command `source local.env`.
9. Run the application by running the following command `python __main__.py`.
