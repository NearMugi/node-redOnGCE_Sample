# Node-RED On GCE (Sample)

Node-RED Running on Google Compute Engine  
Semi-automatic Deployment  

## 今回できること

* VMインスタンスを停止->開始してもNode-REDのフローが消えない  
* VMインスタンスの生成がバッチファイル実行で自動的に行える
* VMインスタンスの起動・停止を管理できる

## GCEインスタンスの環境  

![flow_1](https://user-images.githubusercontent.com/25577827/87436803-7dd00e00-c628-11ea-9862-8933ee377b39.jpg)

* Node-REDはVMインスタンスで動くDockerコンテナ内で動いている
* Node-RED(tcp:1880)にアクセスできるIPアドレスを指定できる
* スケジューラーと組み合わせて起動・停止を管理できる
* ローカル環境と同じように、フォルダ内のファイルにアクセスできる

## 事前準備  

GCEインスタンスを動かすためにGCPでいくつか設定する

### GoogleCloudStorage(GCS)  

VMインスタンスへのアップロード用のバケットを用意する

| 項目                         | 設定                   |
| ---------------------------- | ---------------------- |
| バケット名           | gce-node-red                 |
| ロケーションタイプ           | Region                 |
| ロケーション                 | asia-northeast1 (東京) |
| デフォルトのストレージクラス | Standard               |

![GCS](https://user-images.githubusercontent.com/25577827/87437880-cfc56380-c629-11ea-8d41-2b84ce84f9e3.PNG)

### VPCネットワーク  

Node-RED(tcp:1880)にアクセスできるようにネットワークを用意する  

* ネットワーク  

| 項目                         | 設定                   |
| ---------------------------- | ---------------------- |
| ネットワーク名           | node-red-network                 |
| サブネット作成モード                 | カスタム サブネット |
| 動的ルーティング モード | リージョン              |  

![VPC](https://user-images.githubusercontent.com/25577827/87441541-27fe6480-c62e-11ea-8dc8-bf628f4e3590.PNG)

* サブネットワーク  

| 項目                         | 設定                   |
| ---------------------------- | ---------------------- |
| サブネットワーク名           | node-red-subnetwork                 |
| リージョン                 | asia-northeast1 |
| IP アドレス範囲 | 10.146.0.0/20 ※何でも良いはず              |  

![VPC_2](https://user-images.githubusercontent.com/25577827/87442907-c7702700-c62f-11ea-941e-ad23ca4605d3.PNG)

* ファイアウォール  

| 項目                         | 設定                   |
| ---------------------------- | ---------------------- |
| ファイアウォール名           | node-red-firewall                 |
| ネットワーク                 | node-red-network |
| ターゲットタグ | node-red-network-tag |  
| ソースIPの範囲 | 許可したいグローバルIPアドレス              | 
| 指定したプロトコルとポート | tcpにチェックして1880を指定              | 

![Firewall](https://user-images.githubusercontent.com/25577827/87442984-e1116e80-c62f-11ea-8846-b903710d57c2.PNG)

### ローカル環境でContainer Registryを認証する  

[Docker 認証情報ヘルパーとしての gcloud](https://cloud.google.com/container-registry/docs/advanced-authentication?hl=ja#gcloud-helper)を参照  
以下のコマンドを実行すれば認証される  

```bat
gcloud auth login
gcloud auth configure-docker
```

## GCEにインスタンスを生成するまでの手順

大まかな流れは以下の通り  
![flow_2](https://user-images.githubusercontent.com/25577827/87437418-444bd280-c629-11ea-99e5-303565b4d751.jpg)
1. Node-REDフローを用意する
2. Dockerイメージを作る
3. GCPのContainerRegistryへアップロードする
4. GCSにGCEで使用するファイルをアップロードする
5. GCPのDeploymentManagerを使ってGCEインスタンスを生成する
6. GCEインスタンスが起動する

**2～6はバッチファイル実行で自動的に行われる**  
GCEの起動・停止については「[VMインスタンスの起動/停止を管理する](#VMインスタンスの起動/停止を管理する)」に記述している

### 1. Node-REDフローを用意する  

| ファイル        | 内容                             |
| --------------- | -------------------------------- |
| flows.json      | フロー                           |
| flows_cred.json | 機密情報 ※githubには入っていない |
| package.json    | フローで使用するパッケージの一覧 |
| settings.js     | Node-REDの設定                   |

ローカル環境で動作する[enebular editor](https://docs.enebular.com/ja/EnebularEditor/)でフローを作成するのがおすすめ  
以下のフォルダにflows.json・flows_cred.jsonが保存されている

```bat
C:\Users\[USER]\AppData\Local\Programs\enebular-editor\resources\app\node-red
```

## 2. Dockerイメージを作る  

/node-redInstance内の、docker-compose.yml・/node-red/Dockerfile参照  

## 3. GCPのContainerRegistryへアップロードする

[Container Registry のクイックスタート](https://cloud.google.com/container-registry/docs/quickstart?hl=ja#build_a_docker_image)、[イメージのレジストリへの push](https://cloud.google.com/container-registry/docs/pushing-and-pulling?hl=ja#pushing_an_image_to_a_registry)を参照  

1. ローカルのDockerにイメージを追加する
2. GCP向けのタグをつける
3. ContainerRegistryにアップロードする

``` bat
docker-compose build
docker tag node-redongce_sample_node-red asia.gcr.io/[PROJECT_ID]/node-red
docker push asia.gcr.io/[PROJECT_ID]/node-red
```
ContainerRegistryにDockerイメージが追加される  
![ContainerRegistry](https://user-images.githubusercontent.com/25577827/87438747-e6b88580-c62a-11ea-90a5-e958f5d68acc.PNG)

## 4. GCSにGCEで使用するファイルをアップロードする

事前準備で作成したバケットにアップロードする。
![GCS_2](https://user-images.githubusercontent.com/25577827/87440662-2f713e00-c62d-11ea-8369-a24e465f3481.PNG)  

## 5. GCPのDeploymentManagerを使ってGCEインスタンスを生成する

インスタンスの設定(使用するCPUなど)はyamlファイルにまとめている  
/node-redInstance/DeploymentManager内のファイルを参照  
例えばCPUやリージョンを変更したい、プリエンティブルインスタンスを無効にしたいなどの場合はこちらを編集する  
※詳細は[gcloud または API を使用してデプロイを作成する](https://cloud.google.com/deployment-manager/docs/deployments?hl=ja)を参照

``` bat
gcloud deployment-manager deployments create [DEPLOYMENT_MANAGER_NAME] --config container_vm.yaml
```

DeploymentManagerにデプロイ情報が追加される  
![DeploymentManager](https://user-images.githubusercontent.com/25577827/87438701-d86a6980-c62a-11ea-83cb-2ed171819803.PNG)

GCEにVMインスタンスが追加される  
![GCE](https://user-images.githubusercontent.com/25577827/87438370-642fc600-c62a-11ea-80cc-97199a26cdeb.PNG)

## VMインスタンス生成を自動化  

VMインスタンスの生成を自動化出来るようにしたフォルダを用意した

### フォルダ構成(Instance)  

| フォルダ(orファイル) | 概要                                                 |
| -------------------- | ---------------------------------------------------- |
| node-red             | DockerfileやNode-REDの設定ファイルを格納             |
| docker-compose.yml   | Docker Compose                                       |
| gcs                  | Google Cloud Storageにアップロードするファイルを格納 |
| startupScript        | Docker起動時に実行するファイルを格納                 |
| DeploymentManager    | Cloud Deployment Manager の設定ファイルを格納        |
| deploy.bat           | コンテナをデプロイするバッチファイル                 |

### 初期設定  

GCPのプロジェクトIDに合わせるため、以下のファイルを修正する  

| ファイル                | 修正箇所                                 | 修正内容                        |
| ----------------------- | ---------------------------------------- | ------------------------------- |
| deploy.bat              | set PROJECT_ID="[PROJECT_ID]"            | GCPのプロジェクトIDに置き換える |
| container_manifest.yaml | image: asia.gcr.io/[PROJECT_ID]/node-red | GCPのプロジェクトIDに置き換える |

### デプロイの手順  

1. Node-REDのフローを"node-red"フォルダに追加する  
2. Google Cloud Storageにアップロードするファイルを"gcs"フォルダに格納する
3. 必要に応じてnode-red/package.json、node-red/Dockerfileを編集する
4. deploy.batを実行する  

一度初期設定を行えば、この手順でNode-REDのフローを更新できる

### 補足事項

#### GCSにアップロードしたファイルにアクセスする

GCSにアップロードしたファイルは、"/mnt"フォルダ内に追加されている  
フォルダ構成をそのままコピーするので、もしサブフォルダに入れているのであれば"/mnt/サブフォルダ"となる  
Node-REDでexecノードを使えばアクセスできる

#### Nodeのパッケージをインストールする  

package.jsonにパッケージを記述する

#### Pythonを使う

Dockerfileにパッケージを記述する  
python3は使えるが、pipは入っていないのでpipのインストールから行う  
以下はpandasなどをインストールする例

``` dockerfile  
# install pip
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
ENV PATH $PATH:/usr/src/node-red/.local/bin
RUN pip3 install --upgrade pip setuptools

# install matplotlib numpy pandas
# [reference]https://tech.shiroshika.com/docker-python-pandas-matplotlib/
USER root
RUN apk --update-cache add musl linux-headers gcc g++ make gfortran openblas-dev python3 python3-dev freetype-dev

RUN pip3 install Cython
RUN pip3 install matplotlib
RUN pip3 install numpy
RUN pip3 install pandas

# install pillow
RUN apk --update add libxml2-dev libxslt-dev libffi-dev gcc musl-dev libgcc openssl-dev curl
RUN apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev
RUN pip3 install pillow

# install other python package
RUN pip3 install line-bot-sdk
RUN pip3 install google-api-python-client
```

### 各ファイルの補足

#### deploy.bat  

バッチファイルで以下の処理を行っている

1. GoogleCloudStorageにデータをアップロードする  
a. 一度データを全て削除
b. startup.shをアップロード
c. gsフォルダ内のファイル・フォルダをアップロード
2. ContainerRegistryにDockerイメージをアップロードする  
a. ローカルでDockerイメージを生成  ※このときタグ名が"フォルダ名"_node-redになる
b. 生成したDockerイメージにContainerRegistryへアップロードする用のタグをつける  
c. ContainerRegistryへアップロードする  
3. Cloud Deployment ManagerにGCEへのデプロイ設定を登録する  
a. 前回の設定を削除する  
b. 今回の設定を追加する  

#### container_vm.py  

VMインスタンスの設定を指定する  
ファイル構成については[コンテナ最適化デプロイメントを作成する](https://cloud.google.com/deployment-manager/docs/create-container-deployment?hl=ja#python_2)、各項目については[REST Resource: instances](https://cloud.google.com/compute/docs/reference/rest/v1/instances)を参照  

ポイントを抜粋する

* マシンタイプの指定

``` bat  
"machineType": ZonalComputeUrl(
    context.env["project"],
    context.properties["zone"],
    "machineTypes",
    "g1-small",
)
```

* GCPのサービスアカウントの指定

``` bat
"serviceAccounts": [
    {
        "email": "default",
        "scopes": [
            "https://www.googleapis.com/auth/pubsub",
            "https://www.googleapis.com/auth/logging.write",
            "https://www.googleapis.com/auth/monitoring.write",
            "https://www.googleapis.com/auth/trace.append",
            "https://www.googleapis.com/auth/servicecontrol",
            "https://www.googleapis.com/auth/service.management.readonly",
            "https://www.googleapis.com/auth/devstorage.read_write",
        ],
    }
],
```

* プリエンティブルインスタンスの指定

``` bat
"scheduling": {"preemptible": True},
```

## VMインスタンスの起動/停止を管理する

[Cloud Scheduler + Cloud Pub/Sub + Cloud Functions でGCEのインスタンスの自動起動or停止させてみた](https://qiita.com/uu4k/items/4075acff6ef6a7ed9384) を参考した  

* GoogleCloudFunctions(GCF)にGCEインスタンスの起動・停止を指示するプログラムを追加
* Cloud Schedulerでプログラムを定期的に実行

### フォルダ構成(Schedule)  

| フォルダ(orファイル)          | 概要                                            |
| ----------------------------- | ----------------------------------------------- |
| GCEInstanceTrigger            | GCEインスタンスの起動・停止を指示するプログラム |
| deploy_GCEInstanceTrigger.bat | プログラムをデプロイするバッチファイル          |
| GCEInstanceTrigger.bat        | スケジューラーを設定するバッチファイル          |

### 手順  

scheduleフォルダに入っているバッチファイルを実行する  

1. deploy_GCEInstanceTrigger.bat を実行
2. GCEInstanceTrigger.bat の\[PROJECT_ID]をプロジェクトIDに書き換えて実行  

Cloud SchedulerとGoogleCloudFunctionsにそれぞれ設定(スクリプト)が追加される  
![Schedule](https://user-images.githubusercontent.com/25577827/87439464-c937eb80-c62b-11ea-8023-a26fb2c6f4a3.PNG)  

![GCF](https://user-images.githubusercontent.com/25577827/87439503-d48b1700-c62b-11ea-89ea-7c3439255652.PNG)  

