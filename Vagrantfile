# -*- mode: ruby -*-
# vi: set ft=ruby :

$preProvision= <<SCRIPT
sudo apt-get update && sudo apt-get install tmux python-pip redis -y
pip install pipenv
SCRIPT

$provision= <<SCRIPT
cd /vagrant
pipenv --two install
redis-server
SCRIPT

$startServer= <<SCRIPT
tmux kill-session -t "rss" || true
tmux new -d -n "web" -s "rss" -c "/vagrant" "pipenv run python web.py"
tmux neww -d -n "server" -c "/vagrant" "pipenv run python main.py"
SCRIPT

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-18.04"

  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.network "forwarded_port", guest: 6000, host: 6000

  # Pre-provision
  config.vm.provision "shell", inline: $preProvision

  # Provisioning scripts
  config.vm.provision "shell", inline: $provision, privileged: false

  # Start server in tmux session (every reboot)
  config.vm.provision "shell", inline: $startServer, privileged: false, run: "always"
end
