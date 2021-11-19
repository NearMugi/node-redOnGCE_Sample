@echo off
cd /d %~dp0

set BUCKET="gce-node-red"
echo +++ [Delete GoogleStorage File]
call gsutil -m rm gs://%BUCKET%/**

echo +++ [Upload to GoogleStorage]Startup Script 
call gsutil cp startupScript/startup.sh gs://%BUCKET%/

echo +++ [Upload to GoogleStorage]Docker(Node-Red) Local File
for %%f in (gcs\*) do (
  call gsutil cp %%f gs://%BUCKET%/
)

echo +++ [Upload to GoogleStorage]Docker(Node-Red) Local Folder
for /d %%f in (gcs\*) do (
  call gsutil -m cp -r %%f gs://%BUCKET%/
)

echo +++ [Upload to ContainerRegistry]
set PROJECT_ID="[PROJECT_ID]"
docker-compose build
rem Tag Name of LocalDockerImage is foldername(Lcase) + "_node-red" 
set THIS_PATH=%~dp0
for %%1 in ("%THIS_PATH:~0,-1%") do set FOLDER_NAME=%%~nx1
set TAG_NAME=%FOLDER_NAME%_node-red
for %%i in (a b c d e f g h i j k l m n o p q r s t u v w x y z) do call set TAG_NAME=%%TAG_NAME:%%i=%%i%%
docker tag %TAG_NAME% asia.gcr.io/%PROJECT_ID%/node-red
docker push asia.gcr.io/%PROJECT_ID%/node-red

set DEPLOYMENT_MANAGER_NAME="node-red-container"

echo +++ [Create GCEInstance] Delete Deployment Manager SettingFile(%DEPLOYMENT_MANAGER_NAME%)
echo Y|call gcloud deployment-manager deployments delete %DEPLOYMENT_MANAGER_NAME%

echo +++ [Create GCEInstance] Create Deployment Manager SettingFile(%DEPLOYMENT_MANAGER_NAME%)
cd DeploymentManager
call gcloud deployment-manager deployments create %DEPLOYMENT_MANAGER_NAME% --config container_vm.yaml

pause