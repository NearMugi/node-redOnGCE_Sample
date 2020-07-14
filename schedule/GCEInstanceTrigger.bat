@echo off
rem "GCEInstanceWakeOrSleep : Google Schedulerの名前"
rem "schedule "*/1 * * * *" : 1分ごとに起動"
rem "topic "projects/[PROJECT_ID]/topics/GCEInstance" : Pub/Subのトピック名"
rem "time-zone "Asia/Tokyo" : タイムゾーン"
rem "message-body "{
rem                \"zone\":\"[VMインスタンスのゾーン]\", 
rem                \"project\":\"[PROJECT_ID]\", 
rem                \"instance\":\"[VMインスタンス名]\",
rem                \"enableHourStart\":[起動時間], 
rem                \"enableHourEnd\":[停止時間]
rem                }"

gcloud beta scheduler jobs create pubsub GCEInstanceWakeOrSleep --schedule "*/1 * * * *" --topic "projects/[PROJECT_ID]/topics/GCEInstance" --time-zone "Asia/Tokyo" --description "GCE Instance WakeUp or Sleep Scheduler" --message-body "{\"zone\":\"asia-northeast1-b\", \"project\":\"[PROJECT_ID]\", \"instance\":\"node-red-instance\", \"enableHourStart\":6, \"enableHourEnd\":24}"
