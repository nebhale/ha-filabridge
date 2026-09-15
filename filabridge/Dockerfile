# FilaBridge application version; the wrapper version lives in config.yaml.
FROM ghcr.io/sargonas/filabridge:1.4.0

USER root
RUN apk add --no-cache curl jq nginx

EXPOSE 5000

COPY nginx.conf.template /nginx.conf.template
COPY run.sh /run.sh

RUN chmod +x /run.sh

ARG BUILD_ARCH
ARG BUILD_VERSION

LABEL \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="app" \
    io.hass.version="${BUILD_VERSION}"

ENTRYPOINT ["/run.sh"]
