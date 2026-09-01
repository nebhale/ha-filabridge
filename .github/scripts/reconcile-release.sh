#!/usr/bin/env bash

set -Eeuo pipefail

VERSION="${1:-}"
CONFIG_PATH="filabridge/config.yaml"
REPOSITORY="${GITHUB_REPOSITORY:-nebhale/ha-filabridge}"

if [[ ! "${VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Invalid stable FilaBridge version: ${VERSION}" >&2
  exit 1
fi

TAG="v${VERSION}"
IMAGE="ghcr.io/sargonas/filabridge:${VERSION}"

# Locate the commit that introduced this exact manifest version. The workflow
# reconciles the current version before moving forward, so this remains
# recoverable even if a previous run stopped after pushing the commit.
VERSION_COMMIT="$(
  git log --reverse \
    -S"version: \"${VERSION}\"" \
    --format='%H' \
    -- "${CONFIG_PATH}" | sed -n '1p'
)"

if [[ -z "${VERSION_COMMIT}" ]]; then
  echo "No commit introduces FilaBridge ${VERSION} in ${CONFIG_PATH}" >&2
  exit 1
fi

COMMIT_VERSION="$(
  git show "${VERSION_COMMIT}:${CONFIG_PATH}" |
    sed -nE 's/^version:[[:space:]]*"([^"]+)".*/\1/p'
)"

if [[ "${COMMIT_VERSION}" != "${VERSION}" ]]; then
  echo "Commit ${VERSION_COMMIT} does not contain FilaBridge ${VERSION}" >&2
  exit 1
fi

git fetch --tags origin

if git show-ref --verify --quiet "refs/tags/${TAG}"; then
  TAG_TYPE="$(git cat-file -t "refs/tags/${TAG}")"
  if [[ "${TAG_TYPE}" != "tag" ]]; then
    echo "${TAG} exists but is not an annotated tag" >&2
    exit 1
  fi

  TAG_COMMIT="$(git rev-list -n 1 "refs/tags/${TAG}")"
  if [[ "${TAG_COMMIT}" != "${VERSION_COMMIT}" ]]; then
    echo "${TAG} points to ${TAG_COMMIT}, expected ${VERSION_COMMIT}; refusing to move it" >&2
    exit 1
  fi
else
  git tag -a "${TAG}" "${VERSION_COMMIT}" -m "FilaBridge ${VERSION}"
  git push origin "refs/tags/${TAG}"
fi

if RELEASE_JSON="$(
  gh release view "${TAG}" \
    --repo "${REPOSITORY}" \
    --json isDraft,isPrerelease,tagName,url 2>/dev/null
)"; then
  if ! jq -e \
    --arg tag "${TAG}" \
    '.tagName == $tag and .isDraft == false and .isPrerelease == false' \
    <<<"${RELEASE_JSON}" >/dev/null; then
    echo "GitHub Release ${TAG} exists but is not a published stable release" >&2
    exit 1
  fi

  echo "GitHub Release ${TAG} already exists"
  exit 0
fi

UPSTREAM_URL="$(
  gh api "repos/sargonas/filabridge/releases/tags/${TAG}" --jq '.html_url'
)"

NOTES_FILE="$(mktemp)"
trap 'rm -f "${NOTES_FILE}"' EXIT

printf '%s\n\n' \
  "Updates the Home Assistant App wrapper to FilaBridge ${VERSION}." \
  "- Upstream release: ${UPSTREAM_URL}" \
  "- Container image: \`${IMAGE}\`" \
  "- Architectures: \`linux/amd64\`, \`linux/arm64\`" \
  "- Wrapper commit: \`${VERSION_COMMIT}\`" \
  "" \
  "The container image and application binaries are published by the upstream FilaBridge project; this release contains only Home Assistant packaging metadata." \
  >"${NOTES_FILE}"

gh release create "${TAG}" \
  --repo "${REPOSITORY}" \
  --verify-tag \
  --title "FilaBridge ${VERSION}" \
  --notes-file "${NOTES_FILE}"

echo "Created GitHub Release ${TAG} for ${VERSION_COMMIT}"
