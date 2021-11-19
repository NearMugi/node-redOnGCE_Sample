#! /bin/bash

BASE_FOLDER=/home
BUCKET=gce-node-red

# Baseフォルダが見つかるまで待つ
echo "Wait until folder($BASE_FOLDER) is found ..."
while :
do
  if [ -d $BASE_FOLDER ]; then
    echo "Find BaseFolder($BASE_FOLDER)"
    break
  fi
  sleep 10s
done

# toolboxとマウントされているフォルダに、GCSのファイルをコピーする
# https://cloud.google.com/container-optimized-os/docs/how-to/toolbox
echo "Copy Google Storage -> toolbox Folder(Mount) -> Instance Folder($BASE_FOLDER)"
toolbox gsutil cp -r gs://$BUCKET/ /media/root/home/

