#!/usr/bin/env sh
set -eu

echo "[INFO] Starting FilaBridge Home Assistant App"

FILABRIDGE_PORT=5000

if [ -n "${SUPERVISOR_TOKEN:-}" ]; then
    echo "[INFO] Querying Supervisor API for ingress URL"
    INGRESS_URL="$({
        curl --fail --silent --show-error \
            --header "Authorization: Bearer ${SUPERVISOR_TOKEN}" \
            http://supervisor/addons/self/info |
            jq --raw-output '.data.ingress_url // empty'
    } || true)"

    if [ -n "${INGRESS_URL}" ]; then
        export FILABRIDGE_BASE_PATH="${INGRESS_URL%/}"
        echo "[INFO] FILABRIDGE_BASE_PATH set to ${FILABRIDGE_BASE_PATH}"

        sed "s|__INGRESS_PATH__|${FILABRIDGE_BASE_PATH}|g" \
            /nginx.conf.template >/etc/nginx/nginx.conf

        echo "[INFO] Starting nginx prefix restorer on port 5000"
        if nginx -c /etc/nginx/nginx.conf; then
            sleep 1

            if [ -r /tmp/nginx.pid ] && \
                kill -0 "$(cat /tmp/nginx.pid)" 2>/dev/null; then
                echo "[INFO] nginx started successfully"
                FILABRIDGE_PORT=5001
            else
                echo "[WARN] nginx stopped; using direct mode on port 5000"
                unset FILABRIDGE_BASE_PATH
            fi
        else
            echo "[WARN] nginx failed to start; using direct mode on port 5000"
            unset FILABRIDGE_BASE_PATH
        fi
    else
        echo "[WARN] Could not determine ingress URL; using direct mode"
    fi
else
    echo "[WARN] SUPERVISOR_TOKEN is unavailable; using direct mode"
fi

echo "[INFO] Starting FilaBridge on port ${FILABRIDGE_PORT}"
exec /app/main --port "${FILABRIDGE_PORT}"
