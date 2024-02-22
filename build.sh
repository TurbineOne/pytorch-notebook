docker build \
    -f base.dockerfile \
    -t base-pytorch-notebook:latest .

docker build \
    -f create-user.dockerfile \
    --build-arg BASE_IMAGE=base-pytorch-notebook:latest \
    --build-arg MY_UID="$(id -u)" \
    --build-arg MY_GID="$(id -g)" \
    --build-arg USER=$(whoami) \
    --build-arg HOME=$(echo $HOME) \
    -t user-pytorch-notebook:latest .