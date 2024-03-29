# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Creates a Container VM with the provided Container manifest."""


COMPUTE_URL_BASE = "https://www.googleapis.com/compute/v1/"


def GlobalComputeUrl(project, collection, name):
    return "".join(
        [COMPUTE_URL_BASE, "projects/", project, "/global/", collection, "/", name]
    )


def ZonalComputeUrl(project, zone, collection, name):
    return "".join(
        [
            COMPUTE_URL_BASE,
            "projects/",
            project,
            "/zones/",
            zone,
            "/",
            collection,
            "/",
            name,
        ]
    )


def SubnetworkUrl(region, subnetwork):
    return "".join(["regions/", region, "/subnetworks/", subnetwork])


def GenerateConfig(context):
    """Generate configuration."""

    res = []
    base_name = context.env["name"]

    # Properties for the container-based instance.
    instance = {
        "tags": {"items": ["node-red-network-tag", "http-server", "https-server"]},
        "zone": context.properties["zone"],
        "machineType": ZonalComputeUrl(
            context.env["project"],
            context.properties["zone"],
            "machineTypes",
            "g1-small",
        ),
        "metadata": {
            "items": [
                {
                    "key": "gce-container-declaration",
                    "value": context.imports[context.properties["containerManifest"]],
                },
                {"key": "google-logging-enabled", "value": "true"},
                {"key": "startup-script-url",
                    "value": "gs://gce-node-red-sample/startup.sh"},
            ]
        },
        "disks": [
            {
                "deviceName": "boot",
                "type": "PERSISTENT",
                "autoDelete": True,
                "boot": True,
                "initializeParams": {
                    "diskName": base_name + "-disk",
                    "sourceImage": GlobalComputeUrl(
                        "cos-cloud", "images", context.properties["containerImage"]
                    ),
                },
            }
        ],
        "networkInterfaces": [
            {
                "accessConfigs": [{"name": "external-nat", "type": "ONE_TO_ONE_NAT"}],
                "network": GlobalComputeUrl(
                    context.env["project"], "networks", context.properties["network"]
                ),
                "subnetwork": SubnetworkUrl(
                    context.properties["region"], context.properties["subNetwork"]
                ),
            }
        ],
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
        "scheduling": {"preemptible": True},
    }
    res.append(
        {"name": base_name, "type": "compute.v1.instance", "properties": instance}
    )
    # Resources to return.
    resources = {"resources": res}

    return resources
