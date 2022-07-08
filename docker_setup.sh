apk add --no-cache --update git openssh python3
python3 -m ensurepip
pip3 install --no-cache --upgrade pip setuptools
eval $(ssh-agent)
ssh-add /root/.ssh/id_ed25519
echo 'github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl' >> /etc/ssh/ssh_known_hosts
git config --global user.email "fuwasteven@gmail.com"
git config --global user.name "xnevetx"
git clone --depth=1 git@github.com:xtevenx/ProRankings
cd ProRankings
sh update_charts.sh
