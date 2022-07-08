FROM alpine:latest

COPY --chmod=400 id_ed25519* /root/.ssh/
COPY docker_setup.sh /

CMD ["/bin/sh", "/docker_setup.sh"]
