#!/usr/bin/env bash

function sedeasy {
  sed -i "s/$(echo $1 | sed -e 's/\([[\/.*]\|\]\)/\\&/g')/$(echo $2 | sed -e 's/[\/&]/\\&/g')/g" $3
}

if [[ ${DEBUG} != "" ]]; then
  set -x
fi

set -o errexit
set -o pipefail
set -o nounset

IFS=$'\n\t'

echo "[*] creating 'brains' directory"
if [ ! -d brains ]; then
  mkdir brains
fi

echo "[*] installing required dependencies..."
apt update -yq && \
    apt install --no-install-recommends -yq \
                clang \
                nano \
                python2 \
                python2-dev \
                sqlite \
                libsqlite-dev \
                libffi-dev && \
    apt upgrade -y && \
    apt autoremove -y
pip2 install --upgrade pip -r requirements.txt

echo "[*] project bootstrap finished"
read -r -p "Want to set up your credentials now? [y/N] " cred_setup
if [[ "$cred_setup" =~ ^([yY][eE][sS]|[yY])+$ ]]
then
    read -r -p "[:] client_id: " client_id
    read -r -p "[:] client_secret: " client_secret
    read -r -p "[:] username: " username
    read -r -p "[:] password: " password
    read -r -p "[:] user_agent: " user_agent
    sedeasy 'REDDIT_CLIENT_ID' ${client_id} reddit.py
    sedeasy 'REDDIT_SECRET' ${client_secret} reddit.py
    sedeasy 'REDDIT_USERNAME' ${username} reddit.py
    sedeasy 'REDDIT_PASSWORD' ${password} reddit.py
    sedeasy 'REDDIT_USER_AGENT' ${user_agent} reddit.py
    echo "[*] Setup completed. Run the bot using 'python2 run.py' to double check your credentials check the top of 'nano reddit.py'."
else
    echo "[!] Please setup your credentials in reddit.py using 'nano reddit.py' then run the bot using 'python2 run.py'"
fi
