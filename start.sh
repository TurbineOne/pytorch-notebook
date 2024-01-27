docker run --rm \
    -it \
    --user $UID:$GID \
    --workdir="/home/$USER" \
    -p 8888:8888 \
    --gpus all \
    -e JUPYTER_TOKEN=passwd \
    -v $(pwd)/notebooks:/home/joshua \
    user-pytorch-notebook:latest