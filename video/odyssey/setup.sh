#!/usr/bin/env bash
# Fetch everything the build needs that is not in git: Python deps, ffmpeg, the Kokoro v1.0 voice model
# (Apache-2.0, mirrored on npm), and the Natural Earth II / Moon textures (from the Cesium npm package).
set -euo pipefail
cd "$(dirname "$0")"
pip install -q numpy scipy pillow skia-python onnxruntime kokoro-onnx fonttools brotli
command -v ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg libegl1 libgl1)
mkdir -p .models && cd .models
if [ ! -f kokoro-v1.0-fp32.onnx ]; then
  for s in a b c; do
    curl -sSfL -o $s.tgz https://registry.npmjs.org/kokoro-fp32$s-shards/-/kokoro-fp32$s-shards-1.0.0.tgz
    mkdir -p $s && tar xzf $s.tgz -C $s
  done
  cat $(for i in $(seq 0 18); do ls */package/kokoro-fp32.part$i.bin; done) > kokoro-v1.0-fp32.onnx
  rm -rf a b c ./*.tgz
fi
if [ ! -d voices ]; then
  curl -sSfL -o klr.tgz https://registry.npmjs.org/kokoro-local-runtime/-/kokoro-local-runtime-0.1.0.tgz
  mkdir -p klr && tar xzf klr.tgz -C klr && mv klr/package/voices voices && rm -rf klr klr.tgz
fi
echo "ready: python3 audio.py && python3 render.py"
