XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth
touch $XAUTH
xhost +
xauth nlist :0 | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge -

cd "$(dirname "$0")"
docker-compose up -d --force-recreate
