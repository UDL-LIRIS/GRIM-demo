# An Hera based version of the GRIM project workflow<!-- omit from toc -->

## Table of contents<!-- omit from toc -->

- [Installation](#installation)
- [Building and pushing the container images to a registry](#building-and-pushing-the-container-images-to-a-registry)
- [Allocating cluster level Workflow ressources](#allocating-cluster-level-workflow-ressources)
- [Running the workflow](#running-the-workflow)
- [Accessing results](#accessing-results)
- [References](#references)

## Installation

Note: although the usage of a [(python) virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) is recommandable it remains optional

```bash
cd `git rev-parse --show-toplevel`/Workflow/Hera
python3.10 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt         # Instal dependencies
```

Copy the [`hera.config.tmpl`](./hera.config.tmpl) to `hera.config` and configure that file to your ArgoWorkflows server.

Quick checks of the installation

```bash
python -c "import hera_k8s_utils"      # Checking the hera_k8s_utils dependency
python test_environment.py             # Test AW server with handshake 
```

## Building and pushing the container images to a registry

FIXME: clean up or document the `docker compose build` option that can be useful for building in a minikube context.

**WARNING**: some containers (py3dtilers, that uses IFC support, or ribs for which blender depends on the `bpy` x86_64 binary package) of this workflow have binary dependences. Hence such containers can only be (docker_ build on an x86_64 (processor) architecture and cross building will also fail. Before building you should thus **assert your architecture with the command**

```bash
docker system info --format '{{.Architecture}}'
```

whose **result must be `x86_64`**.

```bash
export REGISTRY=harbor.pagoda.os.univ-lyon1.fr
export REGISTRY_GROUP=vcity
export ORGANISATION=${REGISTRY_GROUP}/grim
# Adapt to your platform (cross building not always needed)
alias docker_build="docker build"
# Login to the platform docker registry
docker login ${REGISTRY}/${REGISTRY_GROUP} --username <my-username>
```

```bash
# Building images
docker_build -t ${ORGANISATION}/ribs:1.0                       https://github.com/VCityTeam/TT-Ribs.git -f Docker/Dockerfile
docker_build -t ${ORGANISATION}/fixobjnormals:1.0              `git rev-parse --show-toplevel`/Docker/FixObjNormalsContext
docker_build -t ${ORGANISATION}/py3dtiles:v7.0.0               https://gitlab.com/py3dtiles/py3dtiles.git#v7.0.0 -f docker/Dockerfile
docker_build -t ${ORGANISATION}/py3dtilers:1.0                 `git rev-parse --show-toplevel`/Docker/Py3dtilersContext
docker_build -t ${ORGANISATION}/offsetthreedtilesettolyon:1.0  https://github.com/VCityTeam/UD-Reproducibility.git#master:Computations/3DTiles/Ribs/OffsetTilesetContext
docker_build -t ${ORGANISATION}/mepp2:1.0                      `git rev-parse --show-toplevel`/Docker/Mepp2Context
docker_build -t ${ORGANISATION}/dgtal:1.0                      `git rev-parse --show-toplevel`/Docker/DgtalContext
docker_build -t ${ORGANISATION}/convertsdptoobj:1.0            `git rev-parse --show-toplevel`/Docker/ConvertSdpToObjContext
docker_build -t ${ORGANISATION}/objtoobjscaleoffset:1.0        `git rev-parse --show-toplevel`/Docker/ObjToObjScaleOffsetContext
docker_build -t ${ORGANISATION}/3dtiles-server:1.0             `git rev-parse --show-toplevel`/Docker/ThreeDTilesSamplesContext
```

```bash
# Tagging for the registry
docker tag ${ORGANISATION}/ribs:1.0                       ${REGISTRY}/${ORGANISATION}/ribs:1.0
docker tag ${ORGANISATION}/fixobjnormals:1.0              ${REGISTRY}/${ORGANISATION}/fixobjnormals:1.0
docker tag ${ORGANISATION}/py3dtiles:v7.0.0               ${REGISTRY}/${ORGANISATION}/py3dtiles:1.0
docker tag ${ORGANISATION}/py3dtilers:1.0                 ${REGISTRY}/${ORGANISATION}/py3dtilers:1.0
docker tag ${ORGANISATION}/offsetthreedtilesettolyon:1.0  ${REGISTRY}/${ORGANISATION}/offsetthreedtilesettolyon:1.0
docker tag ${ORGANISATION}/mepp2:1.0                      ${REGISTRY}/${ORGANISATION}/mepp2:1.0
docker tag ${ORGANISATION}/dgtal:1.0                      ${REGISTRY}/${ORGANISATION}/dgtal:1.0
docker tag ${ORGANISATION}/convertsdptoobj:1.0            ${REGISTRY}/${ORGANISATION}/convertsdptoobj:1.0
docker tag ${ORGANISATION}/objtoobjscaleoffset:1.0        ${REGISTRY}/${ORGANISATION}/objtoobjscaleoffset:1.0
docker tag ${ORGANISATION}/3dtiles-server:1.0             ${REGISTRY}/${ORGANISATION}/3dtiles-server:1.0
```

```bash
# Publishing to the registry
docker push ${REGISTRY}/${ORGANISATION}/ribs:1.0
docker push ${REGISTRY}/${ORGANISATION}/fixobjnormals:1.0
docker push ${REGISTRY}/${ORGANISATION}/py3dtiles:1.0
docker push ${REGISTRY}/${ORGANISATION}/py3dtilers:1.0
docker push ${REGISTRY}/${ORGANISATION}/offsetthreedtilesettolyon:1.0
docker push ${REGISTRY}/${ORGANISATION}/mepp2:1.0
docker push ${REGISTRY}/${ORGANISATION}/dgtal:1.0
docker push ${REGISTRY}/${ORGANISATION}/convertsdptoobj:1.0
docker push ${REGISTRY}/${ORGANISATION}/objtoobjscaleoffset:1.0
docker push ${REGISTRY}/${ORGANISATION}/3dtiles-server:1.0
```

## Allocating cluster level Workflow ressources

```bash
cd $(git rev-parse --show-cdup)//Workflow/Hera
# Reminder for the workspace setting
kubectl config set-context --current --namespace=argo-dev
# Creation of the workflow I/O placeholder (including results)
kubectl apply -f define_pvc_pagoda.yaml
# Assert volume was properly created (the name grim-pvc comes from
# define_pvc_pagoda.yaml):
kubectl get pvc grim-pvc
```

## Running the workflow

```bash
cd $(git rev-parse --show-toplevel)/Workflow/Hera
python grim_workflow.py
```

## Accessing results

Set your namespace

```bash
kubectl config set-context --current --namespace=argo-dev
```

One can

- either browse the results (at shell level) from within an ad-hoc container
  with (refer to [the header](define_zombie_pod_for_PV_navigation_with_bash.yaml)
  for further details)

  ```bash
  cd $(git rev-parse --show-toplevel)/Workflow/Hera
  # Create pod
  k apply -f define_zombie_pod_for_PV_navigation_with_bash.yaml
  # Assert pod was created
  k get pod grim-pvc-ubuntu-pod
  k exec -it grim-pvc-ubuntu-pod -- bash
  # And then `cd /grim-data/` and navigate the directory tree with bash...
  ```

  Eventually (when the work session is over), free the allocated pod

  ```bash
  k delete -f define_zombie_pod_for_PV_navigation_with_bash.yaml
  ```

- or copy the results to the commanding desktop with the following commands

  ```bash
  cd $(git rev-parse --show-cdup)/Workflow/Hera
  k apply -f define_zombie_pod_for_PV_navigation_with_browser.yaml
  kubectl -n cp -r grim-pvc-nginx-pod:/var/lib/www/html/junk/ junk
  k delete -f define_zombie_pod_for_PV_navigation_with_browser.yaml
  ```

  When the pod deletion fails (and appears with "Terminating" status in
  `k get pods`) then forcing the deletion can be done with

  ```bash
  k delete pod grim-pvc-ubuntu-pod --force
  ```

## References

- [Using the ribs tool with docker](https://github.com/VCityTeam/TT-Ribs/tree/master/Docker).
  Examples of [usage of the ribs tool](https://github.com/VCityTeam/UD-Reproducibility/blob/master/Computations/3DTiles/Ribs/Readme.md).
