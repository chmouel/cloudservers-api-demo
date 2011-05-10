rscloud-autofw is a script abstracting the Operating System firewalls and allow you to do a firewall change to a lot of different servers.

The script has been kept very simple and literally allow only to :

- enable the firewall
- disable the firewall
- allow or disallow a port or a network
- see firewall status

The prerequistes are :

- A management server under Ubuntu maverick.
- A supported Operating System for clients which includes :

  * Debian.
  * Ubuntu.
  * RHEL.
  * Fedora

- My patched python-cloudservers library (see below for installs).
- Your SSH key installed on all VM for root users.

Install

- After you have kicked a VM with a Ubuntu maverick and connected to it as root you want first execute intall some prereq packages :

<pre lang="sh">
apt-get update && apt-get -y install python-stdeb git
</pre>

checkout my python-cloudservers library :

<pre lang="sh">
git clone git://github.com/chmouel/python-cloudservers.git
</pre>

after being checked-out you will go into the python-cloudservers directory that has just been created and do this :

<pre lang="sh">
cd python-cloudservers/
python setup.py install
</pre>

this should automatically install all the dependences.

Now you can install my api-demo which include the firewall script :

<pre lang="sh">
cd ../
git clone git://github.com/chmouel/cloudservers-api-demo
</pre>

You need to configure some environemnt variable first which keep information about your rackspace account.

edit your ~/.bashrc (or /etc/environement if you want to make it global) and configure those variable :

<pre>
export RCLOUD_DATACENTER=UK
export UK_RCLOUD_USER="MY_USERNAME"
export UK_RCLOUD_KEY="MY_API_KEY"
export UK_RCLOUD_AURL="https://lon.auth.api.rackspacecloud.com/v1.0"
</pre>

or for the US you would have :

<pre>
export RCLOUD_DATACENTER=UK
export UK_RCLOUD_USER="MY_USERNAME"
export UK_RCLOUD_KEY="MY_API_KEY"
export UK_RCLOUD_AURL="https://auth.api.rackspacecloud.com/v1.0"
</pre>

source the ~/.bashrc or relog into your account to have those accounts set-up you can test it to see if that works by going to :

<pre>
~/cloudservers-api-demo/python
</pre>

and launch the command :

<pre>
./list-servers.py
</pre>

to test if this is working properly (it should list your servers for your DATACENTER)

you are now basically ready to mass update firewall on all servers. 

Let's say you have two web servers named web1 and web2 and two db servers named db1 and db2 and you would like to allow the 80 port on the web servers and 3306 port on the db servers.

You would have to go to this directory :

<pre>
~/cloudservers-api-demo/firewall/
</pre>

and first execute this command to see the help/usages :

<pre>
./fw-control.py --help
</pre>

so let's say to enable the firewall on all the web and db server first you can do :

<pre>
./fw-control.py -s "web db" enable
</pre>

it will connect and enable the firewall on all the servers which match the name web and db.

now let's say we want to enable port 80 on the web :

<pre>
./fw-control.py -s "web" allow port 80
</pre>

if you log into the servers you can check with 

<pre>
iptables -L -n 
</pre>

that it it has been enabled properly.

This is simple enough for you to modify the script to your liking to make it more modular for your specific environement.
