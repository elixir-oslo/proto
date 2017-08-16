#!/usr/bin/env bash

# This script runs the hyperbrowser in a docker environment to
# provides all required library dependencies. 

set -e

#-------------------------------------------------------------------------------

declare -r GALAXY_HTTP_PORT=8080
declare -r DOCKERIMGAGE_NAME="hyperbrowser/gsuite"
declare -r DOCKER_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# we assume DOCKER_DIR is [...]/lib/hb/docs/docker/
declare -r HB_DIR="$( cd "${DOCKER_DIR}/../../../.." && pwd )" 

#-------------------------------------------------------------------------------

# check path to hb/galaxy
if [ ! -f "${HB_DIR}/run.sh" ]; then
  printf "error: run.sh not found in \"%s\"\n" "$HB_DIR" >&2
  exit 1
fi
# check path to dockerfile
if [ ! -f "${DOCKER_DIR}/Dockerfile" ]; then
  printf "error: Dockerfile not found in \"%s\"\n" "$DOCKER_DIR" >&2
  exit 1
fi

#-------------------------------------------------------------------------------

# build docker image
(
  cd "$DOCKER_DIR"
  docker build -t $DOCKERIMGAGE_NAME .
)

#-------------------------------------------------------------------------------

# start docker image
(
  cd "$HB_DIR" && \
  docker run --rm \
    --user $(id -u) \
    -p ${GALAXY_HTTP_PORT} --net=host \
    -v $(pwd):/from_host \
    -ti "$DOCKERIMGAGE_NAME" bash -c "cd /from_host && ./run.sh"
)

