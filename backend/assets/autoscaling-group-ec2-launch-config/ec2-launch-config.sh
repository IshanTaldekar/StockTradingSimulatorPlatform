#!/bin/bash

aws s3 cp s3://cloud-computing-project-website-code-bucket/frontend/ /home/ubuntu/frontend/ --recursive

sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv

cd frontend || exit
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

sudo mv frontendservice.service /etc/systemd/system/frontend.service
sudo systemctl daemon-reload
sudo systemctl start frontend
sudo systemctl enable frontend

sydo apt-get install -y nginx
sudo mkdir /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=US/ST=NEW YORK/L=NYC/O=NYU/OU=NYU/CN=NYU/emailAddress=palak7693@gmail.com"

sudo mv nginx_custom_config /etc/nginx/sites-available/default
sudo systemctl restart nginx