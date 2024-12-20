Copy `config.json.tmpl` to `config.json` and edit it to 

* point to the docker registry where you wish to push,
* provide your credentials (both `user` and `password` fields).
(many thanks to the author of [this issue](https://github.com/GoogleContainerTools/kaniko/issues/887))

```bash
docker run -ti --rm -v `git rev-parse --show-toplevel`/Docker/ObjToObjScaleOffsetContext:/workspace -v `pwd`/config.json:/kaniko/.docker/config.json:ro gcr.io/kaniko-project/executor:latest --dockerfile=dockerfile --destination=harbor.pagoda.os.univ-lyon1.fr/vcity/grim/objtoobjscaleoffset:2.0
```

## TODO

Write an Hera workflow that

1. uses this repository as context (that is the git clone of this repo was previously done)
2. at submission stage, copies the `git rev-parse --show-toplevel`/Docker directory of this repository to PVC of the k8s that this workflow will mount at execution stage e.g. in `junk/sources/Docker`. This can be done in python with the kubernetes wrappers: [refer to this issue](https://stackoverflow.com/questions/59703610/copy-file-from-pod-to-host-by-using-kubernetes-python-client) on how getting this to work.
3. Do the same thing to the previously configurer `config.json` file. Alternatively place harbor's user/password credentials in the workflow auth.py configuration file.
4. at (Argo workflows) execution stage has a task that loops/iterates on `junk/sources/Docker` subdirectories in order to submit each of them to Kaniko (as a container within the workflow) for building and pushing images to harbor. This means we still have to populate harbor.pagoda with Kaniko is order for that workflow to build and push all other images. The build bootstap is thus Kaniko...
