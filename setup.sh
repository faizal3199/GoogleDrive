#!/bin/bash

SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

source $SCRIPTPATH/config.data
echo -e "\033[0;36m--------------- ""$name"" ""$version"" ---------------"
echo "$description"
echo "GitHub Repo: ""$github_link"

#sudo update&&sudo apt-get -y install python-pip
#sudo update&&pip install --upgrade google-api-python-client
echo "THIS TOOLS REQUIRES pip AND Python 2.6 or later"
echo "For more details visit https://developers.google.com/drive/v3/web/quickstart/python"

echo -e "\033[1;33mSetting up at /home/$USER/GoogleDrive"
echo "Creating required Files"

echo "Creating directory ~/GoogleDrive"
mkdir -p ~/GoogleDrive

echo "Creating directory ~/.GoogleDrive"
mkdir -p ~/.GoogleDrive

echo "Creating file ~/.GoogleDrive/old_list.txt"
echo "{}">~/.GoogleDrive/old_list.txt

echo "Creating file ~/.GoogleDrive/ids.txt"
echo "{}">~/.GoogleDrive/ids.txt

echo "Creating file ~/.GoogleDrive/userdata.py"
echo "username = '$USER'">~/.GoogleDrive/userdata.py

echo -e "\033[0;33mCopying from $SCRIPTPATH/server.py to ~/.GoogleDrive"
cp "$SCRIPTPATH"/server.py ~/.GoogleDrive/server.py

echo -e "Copying from $SCRIPTPATH/auth.py to ~/.GoogleDrive"
cp "$SCRIPTPATH"/auth.py ~/.GoogleDrive/auth.py

echo -e "Copying from $SCRIPTPATH/client_secret.json to ~/.GoogleDrive"
cp "$SCRIPTPATH"/client_secret.json ~/.GoogleDrive/auth.py

echo -e "Copying from $SCRIPTPATH/simple.py to ~/.GoogleDrive"
cp "$SCRIPTPATH"/simple.py ~/.GoogleDrive/simple.py

echo "Copying from to $SCRIPTPATH/initial.sh ~/.GoogleDrive"
cp "$SCRIPTPATH"/initial.py ~/.GoogleDrive/initial.py

echo "Copying from to $SCRIPTPATH/config.data ~/.GoogleDrive"
cp "$SCRIPTPATH"/config.data ~/.GoogleDrive/config.data

echo "Copying from to $SCRIPTPATH/setup.py ~/.GoogleDrive"
cp "$SCRIPTPATH"/setup.py ~/.GoogleDrive/setup.py

echo "Copying from to $SCRIPTPATH/sync.py ~/.GoogleDrive"
cp "$SCRIPTPATH"/sync.py ~/.GoogleDrive/sync.py

echo "Copying completed"

echo -e "\033[1;37mSetting up Cron Job"

crontab -l >~/GoogleDrive/tmp/cronjob
echo "#GoogleDrive script **don't edit next line**">>~/tmp/cronjob
echo "*/30 * * * * python /home/$USER/.GoogleDrive/sync.py $USER">>~/tmp/cronjob

crontab ~/tmp/cronjob

echo -e "Initializing script"
python ~/.GoogleDrive/setup.py

echo "Setup Complete"
echo -e "\033[0;31mRemoving temporary files"
rm ~/tmp/cronjob
echo -e "You may delete this files\033[0m"