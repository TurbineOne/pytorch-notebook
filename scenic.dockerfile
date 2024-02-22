FROM nvidia/cuda:12.2.2-base-ubuntu22.04

# Set bash as the default shell
ENV SHELL=/bin/bash

# Create a working directory
WORKDIR /app/

# Build with some basic utilities
RUN apt-get update && apt-get install -y \
    python3-pip \
    apt-utils \
    vim \
    git \
    ffmpeg \
    libsm6 \
    libxext6

# alias python='python3'
RUN ln -s /usr/bin/python3 /usr/bin/python

# build with some basic python packages
RUN pip install \
    ffmpeg-python \
    numpy \
    opencv-python-headless \
    jupyterlab

# Install the google-cloud-cli in order to download the owl_vit checkpoints.
RUN --mount=type=cache,sharing=locked,target=/var/lib/apt \
  --mount=type=cache,sharing=locked,target=/var/cache/apt \
  apt-get update \
  && apt-get -y install apt-transport-https ca-certificates gnupg curl sudo

RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && apt-get update && apt-get install google-cloud-cli

RUN mkdir /checkpoints

# Uncomment this and comment the following block to include the finetune
# checkpoints in the image. I think this is needed for finetuning the model?
# RUN --mount=type=cache,sharing=locked,target=/checkpoints \
#     && gsutil cp gs://scenic-bucket/owl_vit/checkpoints/owl2-b16-960-st-ngrams-curated-ft-lvisbase-ens-cold-weight-05_209b65b /checkpoints/owl_vit \
#     && gsutil cp gs://scenic-bucket/owl_vit/checkpoints/clip_vit_b32_b0203fc /checkpoints/owl_vit_finetune

RUN --mount=type=cache,sharing=locked,target=/checkpoints \
    gsutil cp gs://scenic-bucket/owl_vit/checkpoints/owl2-b16-960-st-ngrams-curated-ft-lvisbase-ens-cold-weight-05_209b65b /checkpoints/owl_vit

# Install torch first so that JAX can overwrite the pinned CUDA version. Since
# CUDA versions are supposed to be backwards compatible, this should be fine.
# https://github.com/google/jax/issues/18172
RUN pip3 install torch tqdm git+https://github.com/openai/CLIP.git

RUN mkdir -p /google

RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \ 
    git clone https://github.com/google-research/scenic.git /google/scenic \
    && pip3 install /google/scenic

RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \ 
    git clone https://github.com/google-research/big_vision.git /google/big_vision \
    && pip3 install -r /google/big_vision/big_vision/requirements.txt

# Install version 0.4.23 of JAX which includes `jax.random.PRNGKeyArray`, which
# is required by `ott-jax==0.3.1`. Install `ott-jax==0.3.1`, which includes the
# `transport` package, which is used by the OwlVit models.
RUN pip3 install -U "jax[cuda12_pip]==0.4.23" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html \
    && pip3 install ott-jax==0.3.1

# start jupyter lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--no-browser"]
EXPOSE 8888
