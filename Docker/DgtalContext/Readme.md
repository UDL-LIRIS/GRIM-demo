# Docker version of Dgtal-based pc2vol

## Concerning the dockerfile

Here is an [alternative (simplified) version of the dockerfile](https://github.com/VCityTeam/UD-Reproducibility/blob/master/Computations/3DTiles/ElaphesCave/DockerContexts/pc2volContext/Dockerfile) 
held in this directory.

## Installation

```bash
docker  build -t grim/dgtal-libigl250-cgal553-release.0b7250e.img  .
```

## Running things

```bash
docker run --rm -i -v "$PWD"/datademo:/datademo grim/dgtal-libigl250-cgal553-release.0b7250e.img  /bin/bash -c "time /home/pc2vol/pc2vol/build/pc2vol -i /datademo/bimba_original_meshlab_normals_v5.xyz --gridstep 0.025 -o /datademo/bimba_original_meshlab_normals_v5.vol"
```

## Execution statistics (for the record)

### Run on bimba_original_meshlab_normals_v5.xyz

```bash
mkdir -p datademo
cp ../../Data/Xyz/bimba_original_meshlab_normals_v5.xyz datademo/
docker run -i --rm -v "$PWD"/datademo:/datademo \
  grim/dgtal-libigl250-cgal553-release.0b7250e.img /bin/bash -c \
  "time /home/pc2vol/pc2vol/build/pc2vol \
    --input /datademo/bimba_original_meshlab_normals_v5.xyz \
    --gridstep 0.025 \
    --output /datademo/bimba_original_meshlab_normals_v5.vol"
```

* Number of resulting voxels: 428340
* Maximum RAM usage: ~0.4GB RAM (although to execution is to fast for assertion)
* Elapsed time: 12s

### armadillo 40K points

```bash
mkdir -p datademo
cp ../../Data/Xyz/armadillo_meshlab_normals_v10.xyz datademo/
docker run -i --rm -v "$PWD"/datademo:/datademo \
  grim/dgtal-libigl250-cgal553-release.0b7250e.img /bin/bash -c \
  "time /home/pc2vol/pc2vol/build/pc2vol \
  --input /datademo/armadillo_meshlab_normals_v10.xyz \
  --gridstep 0.012 \
  --output /datademo/armadillo_meshlab_normals_v10.vol"
```

* Number of resulting voxels: 437784
* Maximum RAM usage: ~6GB
* Elapsed time: ~7'

### tunetgen_n50_15k.xyz

As a general note, `pc2vol` segfaults on any of the `tunetgen_n_*.xyz` files.
Try it out with e.g.

```bash
mkdir -p datademo
cp ../../Data/Xyz/tunetgen_n50_15k.xyz datademo/
docker run -i --rm -v "$PWD"/datademo:/datademo \
  grim/dgtal-libigl250-cgal553-release.0b7250e.img /bin/bash -c \
  "time /home/pc2vol/pc2vol/build/pc2vol \
  --input /datademo/tunetgen_n50_15k.xyz \
  --gridstep 1.5 \
  --output /datademo/tunetgen_n50_15k.vol"
```

* Number of resulting voxels: 392472
* Segmentation fault !
