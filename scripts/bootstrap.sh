#!/bin/bash
# sudo apt-get -y install curl  && bash  <(curl http://www.chmouel.com/pub/bootstrap.sh)
export DEBIAN_FRONTEND=noninteractive
set -e

sudo apt-get -y install locales
sudo locale-gen en_GB.UTF-8
sudo dpkg-reconfigure locales

sudo sed -i '/^%admin/ { s/ALL$/NOPASSWD:ALL/ }' /etc/sudoers

sudo apt-get -y install vim screen zsh-beta git-core exuberant-ctags ack-grep

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

for f in gitconfig gitexclude screenrc;do
    ln -fs ${HOME}/GIT/rc-config/${f} ~/.${f}
done

ln -fs ~/GIT/zsh-config ~/.shell
ln -fs ~/.shell/config/zshrc ~/.zshrc
ln -fs ~/GIT/vim-config ~/.vim
ln -fs ~/.vim/vimrc ~/.vimrc

ln -fs ~/GIT/emacs-config ~/.emacs.d

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
