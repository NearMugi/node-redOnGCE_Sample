from googleapiclient import discovery
from googleapiclient import errors
from oauth2client.client import GoogleCredentials

from datetime import datetime
from pytz import timezone

import json
import base64
import sys


def jdgIsStart(_from, _to):
    """ 起動or停止を時間で切り替える
    """
    isStart = False
    hour = datetime.now(timezone("Asia/Tokyo")).hour
    if hour < 5:
        hour += 24
    if hour >= _from and hour < _to:
        isStart = True

    print("%s hour isStartFlg -> %s" % (hour, isStart))

    return isStart


def chkInstanceStatus(compute, project, zone, instance):
    """ インスタンスの存在チェック＆起動中チェック
    """

    # リストにあるかチェックする
    isExist = False
    instances = list_instances(compute, project, zone)
    if instances is None:
        return isExist, False

    for i in instances:
        if i["name"] == instance:
            isExist = True
    if not isExist:
        return isExist, False

    # インスタンスが起動中かチェックする
    isRun = False
    instanceStatus = (
        compute.instances().get(project=project, zone=zone, instance=instance).execute()
    )

    print("[%s] %s" % (instance, instanceStatus["status"]))
    if instanceStatus["status"] in {"PROVISIONING", "STAGING", "RUNNING"}:
        isRun = True

    return isExist, isRun


def list_instances(compute, project, zone):
    """ インスタンスをリストアップ
    """
    result = compute.instances().list(project=project, zone=zone).execute()
    return result["items"] if "items" in result else None


def gceInstancePubSub(event, context):
    """ GCE Instance Start or Stop
        指定した時間範囲により、起動するか停止するかを判断する
        5:00で切り替え。つまり5:00～26:59の範囲。
    """
    # ゾーン・インスタンス名・起動時間の範囲を指定する
    # もし強制的に起動or停止を指定したい場合は"isForce"(Start/Stop)を指定する
    # [sample]
    # {
    #  "zone":"my-zone",
    #  "project":"my-project",
    #  "instance":"my-instance",
    #  "enableHourStart":6,
    #  "enableHourEnd":24
    # }

    if "data" not in event:
        sys.exit(1)

    payload = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    print(payload)

    # 起動or停止を判断する
    isStart = jdgIsStart(payload["enableHourStart"], payload["enableHourEnd"])

    # 強制的に起動(停止)するか判断する
    if "isForce" in payload:
        if payload["isForce"] == "Start":
            isStart = True
        elif payload["isForce"] == "Stop":
            isStart = False

    credentials = GoogleCredentials.get_application_default()
    compute = discovery.build(
        "compute", "v1", credentials=credentials, cache_discovery=False
    )
    project = payload["project"]
    zone = payload["zone"]
    instance = payload["instance"]

    isExistInstance, isRunInstance = chkInstanceStatus(compute, project, zone, instance)

    # 存在しない場合は何もしない
    if not isExistInstance:
        print("[%s] Not Exists..." % instance)
        return

    # 起動中＆起動指示の場合は何もしない
    if isRunInstance and isStart:
        print("[%s] Already Running" % instance)
        return

    # 停止中＆停止指示の場合は何もしない
    if not isRunInstance and not isStart:
        print("[%s] Already Stoped" % instance)
        return

    if isStart:
        print("[%s] Change STOPPED -> RUNNING" % instance)
        try:
            compute.instances().start(
                project=project, zone=zone, instance=instance
            ).execute()
        except errors.HttpError as e:
            print(e)
    else:
        print("[%s] Change RUNNING -> STOPPED" % instance)
        try:
            compute.instances().stop(
                project=project, zone=zone, instance=instance
            ).execute()
        except errors.HttpError as e:
            print(e)
