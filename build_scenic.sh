docker build \
    -f scenic.dockerfile \
    -t scenic-notebook:latest .

docker build \
    -f create-user.dockerfile \
    --build-arg BASE_IMAGE=scenic-notebook:latest \
    --build-arg MY_UID="$(id -u)" \
    --build-arg MY_GID="$(id -g)" \
    --build-arg USER=$(whoami) \
    --build-arg HOME=$(echo $HOME) \
    -t user-scenic-notebook:latest .