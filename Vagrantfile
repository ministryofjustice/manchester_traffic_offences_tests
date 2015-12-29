# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = 2

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.ssh.forward_agent = true

    config.vm.box = "ubuntu/trusty64"
    config.vm.network :forwarded_port, guest: 8888, host: 8888

    config.vm.synced_folder ".", "/vagrant", mount_options: ["dmode=777,fmode=777"]

    config.vm.provider "virtualbox" do |v|
        v.memory = 1024
        v.cpus = 2
    end

    config.vm.provision :shell do |sh|
        sh.privileged = false
        sh.path = "bootstrap.sh"
    end
end
