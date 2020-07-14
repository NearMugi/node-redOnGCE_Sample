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

# toolbox内に"bucket"フォルダを作成、そこにstorageのデータをコピー
# "bucket"フォルダはインスタンス内の"/BASE_FOLDER/gce-node-red"と紐づいている。
# https://stackoverflow.com/questions/55773739/how-to-attach-bucket-to-google-compute-engine-vm-on-startup
echo "Copy Google Storage -> toolbox Folder(Mount) -> Instance Folder($BASE_FOLDER)"
toolbox --bind=$BASE_FOLDER:/bucket <<< "gsutil cp -r gs://$BUCKET/ /bucket/"
