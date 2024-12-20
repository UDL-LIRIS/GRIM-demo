Copy `config.json.tmpl` to `config.json` and edit it to 

* point to the docker registry where you wish to push,
* provide your credentials (both `user` and `password` fields).
(many thanks to the author of [this issue](https://github.com/GoogleContainerTools/kaniko/issues/887))

```bash
docker run -ti --rm -v `git rev-parse --show-toplevel`/Docker/ObjToObjScaleOffsetContext:/workspace -v `pwd`/config.json:/kaniko/.docker/config.json:ro gcr.io/kaniko-project/executor:latest --dockerfile=dockerfile --destination=harbor.pagoda.os.univ-lyon1.fr/vcity/grim/objtoobjscaleoffset:2.0
```
