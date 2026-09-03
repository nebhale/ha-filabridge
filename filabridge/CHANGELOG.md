# Changelog

## 1.3.1-pr.51

- Use the multi-architecture image built from FilaBridge PR #51.
- Add native Home Assistant Ingress and sidebar support.
- Discover the generated Ingress URL at startup and restore its stripped prefix
  before forwarding requests to FilaBridge.
