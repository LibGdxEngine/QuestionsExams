#!/bin/bash
# set HOSTINGER_IP_ADDRESS=31.220.51.27
# export HOSTINGER_IP_ADDRESS=93.127.203.112
if [ -z "$HOSTINGER_IP_ADDRESS" ]
then
  echo "HOSTINGER_IP_ADDRESS not defined"
  exit 0
fi

git archive --format tar --output ./project.tar master

echo 'Uploading project.......:-)...Be Patient!'
rsync ./project.tar root@$HOSTINGER_IP_ADDRESS:/tmp/project.tar
echo 'Upload complete...:-)'

echo 'Building the image...'
ssh -o StrictHostKeyChecking=no root@$HOSTINGER_IP_ADDRESS << 'ENDSSH'
  mkdir -p /app
  rm -rf /app/* && tar -xf /tmp/project.tar -C /app
  docker compose -f /app/production.yml up --build -d --remove-orphans
ENDSSH
echo 'Build completed successfully....:-)'