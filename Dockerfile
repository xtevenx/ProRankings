FROM ubuntu:latest

COPY --chmod=400 id_ed25519* /root/.ssh/

RUN apt-get -y update && \
    apt-get -y --no-install-recommends install git openssh-server python3 python3-pip && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/* && \
    eval $(ssh-agent) && \
    ssh-add /root/.ssh/id_ed25519 && \
    echo 'github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl' >> /etc/ssh/ssh_known_hosts && \
    git config --global user.email "[[REPLACE ME!]]@gmail.com" && \
    git config --global user.name "xnevetx" && \
    git clone git@github.com:xtevenx/ProRankings && \
    cd ProRankings && \
    sh update_charts.sh

WORKDIR /ProRankings

CMD ["/bin/sh", "update_charts.sh"]
