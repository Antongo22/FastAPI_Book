#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

base_image="${BASE_IMAGE:-python:3.12-slim}"
pull_retries="${DOCKER_PULL_RETRIES:-4}"
pull_sleep="${DOCKER_PULL_SLEEP:-5}"
parallel_limit="${COMPOSE_PARALLEL_LIMIT:-1}"

pull_base_image() {
    if [[ "${FORCE_PULL_BASE_IMAGE:-0}" != "1" ]] && docker image inspect "$base_image" >/dev/null 2>&1; then
        echo "Base image is already local: $base_image"
        return 0
    fi

    for attempt in $(seq 1 "$pull_retries"); do
        echo "Pulling base image $base_image (attempt $attempt/$pull_retries)..."
        if docker pull "$base_image"; then
            return 0
        fi

        if [[ "$attempt" == "$pull_retries" ]]; then
            cat <<EOF
Docker could not pull $base_image.

This is usually a Docker Hub/network problem, for example:
  TLS handshake timeout
  failed to resolve source metadata

Try again later, check Docker Desktop networking, or pull the image manually:
  docker pull $base_image

After the image is pulled once, run this script again:
  ./scripts/compose-up.sh
EOF
            return 1
        fi

        sleep "$pull_sleep"
    done
}

pull_base_image

COMPOSE_PARALLEL_LIMIT="$parallel_limit" docker compose --parallel "$parallel_limit" up --build --force-recreate "$@"
