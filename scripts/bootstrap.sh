#!/bin/bash
# sudo apt-get -y install curl  && bash  <(curl http://www.chmouel.com/pub/bootstrap.sh)
version=$(lsb_release -c -s)
export DEBIAN_FRONTEND=noninteractive
set -e

sudo apt-get -y install locales
sudo locale-gen en_GB.UTF-8
sudo dpkg-reconfigure locales

sudo sed -i '/^%sudo/ { s/ALL$/NOPASSWD:ALL/ }' /etc/sudoers


if [[ ${version} == natty || ${version} == oneiric ]];then
    # Old School CS
    sudo sed -i '/^deb.*main/ { /restricted$/ { s/$/ multiverse/; }}' /etc/apt/sources.list 
    # New School CS
    sudo sed  -i '/^#deb .*\(multiverse\|universe\)$/ { s/^#//; }' /etc/apt/sources.list
    sudo apt-get update
fi
sudo apt-get -y install vim tmux screen git-core exuberant-ctags  zsh-beta ack-grep


sudo update-alternatives --set editor /usr/bin/vim.basic

sudo chsh -s /bin/zsh $USER

sudo apt-get -y install ufw && \
    sudo ufw allow proto tcp from any to any port 22 && \
    sudo ufw -f enable

cd $HOME
mkdir -p GIT
cd GIT

for repo in rc zsh vim emacs;do
    git clone git://github.com/chmouel/${repo}-config.git
done

for f in gitconfig gitexclude screenrc tmux.conf;do
    ln -fs GIT/rc-config/${f} ~/.${f}
done

ln -fs GIT/zsh-config ~/.shell
ln -fs .shell/config/zshrc ~/.zshrc
ln -fs GIT/vim-config ~/.vim
ln -fs .vim/vimrc ~/.vimrc

ln -fs GIT/emacs-config ~/.emacs.d

echo -e "#\n#hostColor=\"yellow\"\n#userColor=\"white\"\n" > ~/.shell/hosts/${HOSTNAME%%.*}.sh

cat <<EOF>~/.shell/hosts/${HOSTNAME%%.*}.sh
# hostColor="yellow"
# userColor="white"

alias inst="apt-get -y install"
alias remove="apt-get -y remove"
alias g="ack-grep --color-match 'bold blue'"
alias -g SP="|curl -F 'sprunge=<-' http://sprunge.us"

export LESS="-r"
EOF
