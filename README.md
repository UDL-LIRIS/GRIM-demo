# GRIM-demo

Positioning within the job-scheduler/batch-workflow/data-orchestrator/workflow-orchestrator ecosystem
(reference: [A Brief History of Workflow Orchestration](https://www.prefect.io/blog/brief-history-of-workflow-orchestration))

| Generations  | Install everything<br>(command-scripting) | grim-run.sh<br>(docker-scripting) | `demo_grim_k8s.yaml`<br>k8s | `grim_demo.py`Hera |
| -------- | :-------: |  :-------: |  :-------: | :-------: |
| Becoming mainstream | [1970 (Epoch)](https://en.wikipedia.org/wiki/Epoch_(computing)) | [2015](https://en.wikipedia.org/wiki/Docker_(software)#Adoption) | [2018](https://www.aquasec.com/blog/kubernetes-history-how-it-conquered-cloud-native-orchestration/#section-9) | [2023 (Hera)](https://github.com/argoproj-labs/hera/tree/5.0.0)<br> [2020 (ArgoWorkflows)](https://github.com/argoproj/argo-workflows/tree/v2.0.0-beta1) |
| Desktop installed Tools |||||
| Build/run ecosystems <br> **for all** the components | **X** | | | |
| Sh             | **X** | **X** | **build** (opt)| |
| Python         |       | **X** |                | **X** |
| docker         |       | **X** | **build**      | **opt** ([Kaniko](https://github.com/GoogleContainerTools/kaniko)) |
| kubectl        |       |       | **X**          | **X** |
| Desktop        | **X** | **X** | **devel**          | **devel** |
| Server (cluster) |     |       | **X**          | **X** |
| Workflow Topology | Linear | Linear | Linear | [DAG](https://en.wikipedia.org/wiki/Directed_acyclic_graph) |
| Limits | Package dependency war | Learning curve: `*` | Learning curve: `**` | Learning curve: `***` |

References:
