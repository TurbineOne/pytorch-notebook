docker build \
    -f base-devel.dockerfile \
    -t base-devel-notebook:latest .

docker build \
    -f create-user.dockerfile \
    --build-arg BASE_IMAGE=base-devel-notebook:latest \
    --build-arg MY_UID="$(id -u)" \
    --build-arg MY_GID="$(id -g)" \
    --build-arg USER=$(whoami) \
    --build-arg HOME=$(echo $HOME) \
    -t user-devel-notebook:latest .