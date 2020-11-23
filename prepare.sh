wget https://packages.microsoft.com/config/ubuntu/16.04/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update

sudo apt-get install blobfuse htop iftop

sudo mkdir /mnt/resource/blobfusetmp -p
sudo chown t-zhuyao /mnt/resource/blobfusetmp

echo "accountName vlpretraineastus
accountKey B5/ZEhvIUh0XE1BDai82ooZuEX40GxWVp2T88iARBgpzwOn19NTKFP/3UgoPaGjxw9qTeRAS2t+Z0NqGhBSRBA==
containerName kinetics700" > ~/fuse_connection.cfg
chmod 600 fuse_connection.cfg

if ! [ -f ~/mycontainer ]; then
mkdir ~/mycontainer
fi

sudo blobfuse ~/mycontainer --tmp-path=/mnt/resource/blobfusetmp  --config-file=/home/t-zhuyao/fuse_connection.cfg -o attr_timeout=240 -o entry_timeout=240 -o negative_timeout=120 -o allow_other

echo "Already mounted"

sudo curl -L https://github.com/l1ving/youtube-dl/releases/latest/download/youtube-dl -o /usr/local/bin/youtube-dl
sudo chmod a+rx /usr/local/bin/youtube-dl

sudo apt install -y python3-pip
pip3 install --upgrade setuptools
pip3 install joblib