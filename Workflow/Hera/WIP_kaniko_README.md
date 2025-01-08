# Building the images through Kaniko<!-- omit from toc -->

## Table of contents<!-- omit from toc -->

- [The goal](#the-goal)
- [Notes: a manual example](#notes-a-manual-example)
- [Sub-goal: copy the (build) Contexts from local to (Kaniko) pod](#sub-goal-copy-the-build-contexts-from-local-to-kaniko-pod)
  - [Plan A (FAIL): use the k8s python client](#plan-a-fail-use-the-k8s-python-client)
  - [Plan B (FAIL): provide a container holding and writing the Contexts copy](#plan-b-fail-provide-a-container-holding-and-writing-the-contexts-copy)
  - [Plan C (FAIL): have Hera embark the Contexts at submission stage](#plan-c-fail-have-hera-embark-the-contexts-at-submission-stage)
  - [Plan D (FAIL): plan C with a `pydantic` parameter](#plan-d-fail-plan-c-with-a-pydantic-parameter)
  - [Plan E (FAIL): plan C with a closure](#plan-e-fail-plan-c-with-a-closure)

## The goal

Avoid having to install docker on the local host. For this write an Hera workflow that

1. uses this repository as working/submission context (that is the git clone of this repo was previously done)
2. uses a previously configured `kaniko.json` file, where harbor's user/password credentials have been configured. 
3. at run-time loops/iterates on `git rev-parse --show-toplevel`/Docker (Contexts) subdirectories in order to submit each of them to Kaniko (used as a container within the workflow) for building and pushing images to harbor. 

Notes:

- this strategy implies that we still have to populate harbor.pagoda with Kaniko is order for that workflow to build and push all other images. The build bootstrap is thus based on having an accessible Kaniko...
- an implicit sub-goal is to copy the Contexts from local to the Kaniko pods (refer below)

## Notes: a manual example

Copy `config.json.tmpl` to `config.json` and edit it to

- point to the docker registry where you wish to push,
- provide your credentials (both `user` and `password` fields).
(many thanks to the author of [this issue](https://github.com/GoogleContainerTools/kaniko/issues/887))

```bash
docker run -ti --rm -v `git rev-parse --show-toplevel`/Docker/ObjToObjScaleOffsetContext:/workspace -v `pwd`/kaniko.json:/kaniko/.docker/config.json:ro gcr.io/kaniko-project/executor:latest --dockerfile=dockerfile --destination=harbor.pagoda.os.univ-lyon1.fr/vcity/grim/objtoobjscaleoffset:2.0
```

## Sub-goal: copy the (build) Contexts from local to (Kaniko) pod

We here suppose that the reference Contexts are on a local filesystem (a directory coming resulting from a `git clone` of this repository).
The Kaniko containers (one for each of the Contexts) will need to have at hand (that is within the pod) the build contexts at the Workflow running/execution stage.
We thus need to (recursively) copy the content of the local `git rev-parse --show-toplevel`/Docker directory to the (Kaniko) pods filesystems.
The question is then: how to achieve this with Hera

### Plan A (FAIL): use the k8s python client

The strategy: at Workflow submission stage (that is when running the Hear-Python script), use the python Kubernetes client in order to realize the copy.
One could for example use [this StackOverflow issue](https://stackoverflow.com/questions/59703610/copy-file-from-pod-to-host-by-using-kubernetes-python-client) to realize this copy.
But the difficulty is that such copies do not copy to a Persistent Volume Claim (PVC) but to an existing pod (that uses that PVC). This scheme would thus requires to first create the ad-hoc pod (through the Python client but still at the k8s level) and, once the copy done, to remove that technical temporary pod.
Notice that such copies generally use a (subsystem) command that require a local installation of the `tar` command.
We thus removed the `docker` local dependency but added a `tar` (local) dependency.

### Plan B (FAIL): provide a container holding and writing the Contexts copy

At container build stage, we could embark (with a COPY directive) within an ad-hoc copy container the content of the `git rev-parse --show-toplevel`/Docker directory to the PVC used by the Hera building workflow (that would then use the PVC for Kaniko containers to mount).

Obviously, this is not an acceptable strategy because building such a copy container image needs to be done on the client (thus requiring a docker install) which we precisely wish to avoid.

### Plan C (FAIL): have Hera embark the Contexts at submission stage

The trick is to use as Hera task parameter a variable holding the (in memory) content of the Contexts directory tarball. This was implemented and can be run as follows

```bash
python WIP_kaniko_copy_contexts_with_script_parameter_FAIL.py
```

which fails (at runtime) with the following error message

```bash
Object of type BytesIO is not JSON serializable (type=type_error)
```

The difficulty is that the `io.BytesIO` type (used to encode the tarball within a Python variable) is not supported by AW as a parameter type.

### Plan D (FAIL): plan C with a `pydantic` parameter

Since plan C fails because a `io.BytesIO` variable is not JSON serializable, we might wish to use [RunnerScriptConstructor](https://hera.readthedocs.io/en/5.14.0/user-guides/scripts/#runnerscriptconstructor) to define allowing the "script-decorated function can call other functions in the package".

Alas, this is bound to fails for two reasons:

- first as stated in Hera documentation the [use of the RunnerScriptConstructor necessitates building your own image](https://hera.readthedocs.io/en/5.14.0/user-guides/scripts/#runnerscriptconstructor),
- the usage of [`io.BytesIO` as `pydantic` is not trivial](https://github.com/pydantic/pydantic/issues/5443).

### Plan E (FAIL): plan C with a closure

This was implemented as follows

```bash
python WIP_kaniko_copy_contexts_with_script_closure_FAIL.py
```

which fails (at runtime) with the following error message

```bash
NameError: name 'tarfile_as_bytes' is not defined
```

Well, the [closure](https://en.wikipedia.org/wiki/Closure_(computer_programming) of the `expand_context_to_pvc` function looks empty.


