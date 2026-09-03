FROM ghcr.io/nebhale/filabridge:1.3.1-pr.51

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
