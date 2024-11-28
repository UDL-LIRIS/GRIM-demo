# Testing the container

This directory is a sandbox made for testing this container algorithm.

## Running the tests manually

```bash
cd `git rev-parse --show-toplevel`/Docker/ConvertSdpToObj/Test
docker run -v $(pwd):/io_dir --rm -it grim/convert-sdp-to-obj --input_file /io_dir/skeleton_origin.sdp
# Following diff must return no difference
diff skeleton_origin.obj reference-skeleton_origin.obj
```

## How the files were generated

* The file `skeleton_origin.sdp` is some arbitrary output of the skeleton extraction algorithm.
* The the following commands were applied
  
  ```bash
  cd `git rev-parse --show-toplevel`/Docker/ConvertSdpToObj/Test
  docker run -v $(pwd):/io_dir --rm -it grim/convert-sdp-to-obj --input_file /io_dir/skeleton_origin.sdp --output_file /io_dir/reference-skeleton_origin.obj
  ```
