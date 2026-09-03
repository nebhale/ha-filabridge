# Changelog

## 1.3.1-pr51-2

- Publish the Home Assistant wrapper as a multi-architecture GHCR image.
- Build each release image automatically from its matching Git tag.
- Normalize Home Assistant App metadata before validating the release tag.

## 1.3.1-pr51-1

- Add the initial tag-driven wrapper-image publishing workflow.

## 1.3.1-pr.51

- Use the multi-architecture image built from FilaBridge PR #51.
- Add native Home Assistant Ingress and sidebar support.
- Discover the generated Ingress URL at startup and restore its stripped prefix
  before forwarding requests to FilaBridge.
