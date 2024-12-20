# GRIM-demo

Positioning within the job-scheduler/batch-workflow/data-orchestrator/workflow-orchestrator ecosystem
(reference: [A Brief History of Workflow Orchestration](https://www.prefect.io/blog/brief-history-of-workflow-orchestration))

| Generations  | Install everything<br>(command [shell scripting](https://en.wikipedia.org/wiki/Shell_script)) | grim-run.sh<br>([Docker](https://en.wikipedia.org/wiki/Docker_(software))-based scripting) | `demo_grim_k8s.yaml`<br>([Kubernetes](https://en.wikipedia.org/wiki/Kubernetes)) | `grim_demo.py`<br>([Hera](https://github.com/argoproj-labs/hera)) |
| -------- | :-------: |  :-------: |  :-------: | :-------: |
| Becoming mainstream | [1970 (Epoch)](https://en.wikipedia.org/wiki/Epoch_(computing)) | [2015](https://en.wikipedia.org/wiki/Docker_(software)#Adoption) | [2018](https://www.aquasec.com/blog/kubernetes-history-how-it-conquered-cloud-native-orchestration/#section-9) | [2023 (Hera)](https://github.com/argoproj-labs/hera/tree/5.0.0)<br> [2020 (ArgoWorkflows)](https://github.com/argoproj/argo-workflows/tree/v2.0.0-beta1) |
| **REQUIREMENTS**<br>Installed Tools |||||
| Build/run ecosystems <br> **for all** the components | **X** | | | |
| Sh             | **X** | **X** | **opt**<br>(build script)| |
| Python         |       | **X** |                | **X** |
| docker         |       | **X** | **build**      | **opt**<br>([Kaniko](https://github.com/GoogleContainerTools/kaniko)) |
| kubectl        |       |       | **X**          |  |
| Desktop        | **X** | **X** | **devel**<br>([minikube](https://github.com/kubernetes/minikube)) | **devel**<br>([minikube](https://github.com/kubernetes/minikube)) |
| K8s cluster    |     |       | **X**          | **X**<br>([Argo Server](https://github.com/argoproj/argo-helm)) |
| **ADDITIONAL INFO** |||||
| Workflow Topology | Linear | Linear | Linear | [DAG](https://en.wikipedia.org/wiki/Directed_acyclic_graph)<br>([Parallelism](https://en.wikipedia.org/wiki/Parallel_computing)) |
| Pros/[Cons](https://en.wiktionary.org/wiki/con#Noun) | Package dependency war | Learning curve: `*` | Learning curve: `**` | Learning curve: `***` |
