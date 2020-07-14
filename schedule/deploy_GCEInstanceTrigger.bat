@echo off
rem フォルダ移動
cd /d %~dp0\GCEInstanceTrigger

rem "GCEInstanceTrigger : 関数名"
rem "entry-point gceInstancePubSub : 関数内の呼び出す関数名"
rem "trigger-topic GCEInstance : Pub/Subのトピック"
rem "region asia-northeast1 : リージョン"
gcloud functions deploy GCEInstanceTrigger --runtime python37 --entry-point gceInstancePubSub --trigger-topic GCEInstance --region asia-northeast1