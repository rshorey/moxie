Installation for AWS Debian Jessie
==================================


Security Groups
---------------

Make sure port 80 is usable (for the web UI) and port 2222 (for the SSH
management interface), and in the SGs for PostgreSQL and MongoDB servers as
appropriate and necessary.


Notes
-----

I highly encourage using Docker with `overlay`, not `aufs`, `btrfs`, nor
`devicemapper`. This requires kernel 3.18+; so we'll have to fix that. Feel free
to not do that and use `aufs` if you'd like.


Initial Setup
-------------

    # apt-get update
    # apt-get dist-upgrade -y

Great. Now we need to install some experimental stuff. Literally. The Debian
Kernel for 3.18 is only present in the `experimental` / `rc-buggy` suite
(because of the Jessie freeze), so let's roll with that.

    # nano /etc/apt/sources.list

Append:

    deb http://cloudfront.debian.net/debian experimental main
    deb-src http://cloudfront.debian.net/debian experimental main

to the file. Now let's install the new kernel:

    # apt-get update && apt-get install linux-image-3.18
    # update-grub

Now, let's bounce the instance (from the AWS console run
Actions -> Instance State -> Reboot)

Wait a hot second, and ssh back in. Let's ensure the kernel's running:

    # uname -a
    Linux ip-10-111-189-167 3.18.0-trunk-amd64 #1 SMP Debian 3.18.3-1~exp1 (2015-01-18) x86_64 GNU/Linux

Fannntastic. Now, let's set up the EBS.

    # mkfs.ext4 /dev/xvdf
    # mkdir /projects
    # nano /etc/fstab

and append:

    /dev/xvdf /projects ext4 defaults 1 1

Now mount:

    # mount /projects
    # ln -s /projects/docker /var/lib/docker
    # mkdir /projects/docker

Yay. OK. So; let's get Docker installed. This is a little unorthodox because we
need `overlay` support which is only in Docker 1.4+ and the `docker.io` package
is still 1.3.3 (because of the Jessie freeze).  If you don't need overlay
support (because you opted for `aufs`, `btrfs`, or `devicemapper`), you can skip
the bit here where we download `docker-latest`.

    # apt-get install docker.io
    # usermod -a -G docker admin
    $ # stop here if you don't need "overlay" :)
    $ wget https://get.docker.com/builds/Linux/x86_64/docker-latest -O docker
    $ chmod +x docker
    # cp docker /usr/bin/docker
    # nano /etc/default/docker

Set content to:

    DOCKER_OPTS="-H unix:///var/run/docker.sock -s overlay"

Great; now let's restart:

    # service docker restart

And, log out and back in to see your new group (check with `groups(1)`)

Now, let's verify the setup:

    # docker info | grep Storage
    Storage Driver: overlay


Configuration for Moxie
=======================

I'm going to run the PostgreSQL db on the same host as the moxie runtime for
now. Eventually this will change.

    # apt-get install postgresql-9.4
    # su postgres
    % psql
    postgres=# CREATE ROLE moxie WITH LOGIN PASSWORD 'moxie';
    CREATE ROLE
    postgres=# CREATE DATABASE moxie OWNER moxie;
    CREATE DATABASE
    postgres=# 

Huzzah. Also, feel free to change your login information to not be that.

Let's start the setup:

    # mkdir /etc/docker/
    # nano /etc/docker/moxie.sh

..

    DATABASE_URL=postgres://moxie:moxie@172.17.42.1:5432/moxie
    # MOXIE_SOCKET="/sockets/moxie.sock"
    MOXIE_SLACKBOT_KEY="sec-retkeyhere"
    MOXIE_WEB_URL="http://moxie.sunlightfoundation.com"


Edit `/etc/systemd/system/moxie.service`, and let's just get something
basic working here.

    [Unit]
    Description=moxie
    Author=Paul R. Tagliamonte <tag@pault.ag>
    Requires=docker.service
    After=docker.service
    
    [Service]
    Restart=always
    ExecStart=/bin/bash -c '/usr/bin/docker start -a moxie || \
        /usr/bin/docker run \
            --privileged=true \
            --name moxie \
            -p 0.0.0.0:2222:2222/tcp \
            -p 0.0.0.0:80:8888/tcp \
            -e MOXIE_SLACKBOT_KEY=${MOXIE_SLACKBOT_KEY} \
            -e DATABASE_URL=${DATABASE_URL} \
            -e MOXIE_WEB_URL=${MOXIE_WEB_URL} \
            -v /run/docker.sock:/run/docker.sock \
            -v /srv/docker/moxie/moxie:/moxie/ \
            paultag/moxie:latest moxied'
    ExecStop=/usr/bin/docker stop -t 5 moxie
    EnvironmentFile=/etc/docker/moxie.sh
    
    [Install]
    WantedBy=multi-user.target

Now, let's update

    # systemctl daemon-reload
