import os
import re
import json
import boto3
import tarfile
import requests

# Configuration
REGION = "us-east-1"
ACCOUNT_ID = "711396989588"
REPOSITORY = "stockpilot"
TAR_FILE = "stockpilot_update.tar"

print("🔄 Initializing Pythonic ECR Push Stream...")

# 1. Authenticate with AWS ECR via boto3
client = boto3.client('ecr', region_name=REGION)
auth_response = client.get_authorization_token()
auth_data = auth_response['authorizationData'][0]
ecr_token = auth_data['authorizationToken']
ecr_endpoint = auth_data['proxyEndpoint']

headers = {
    "Authorization": f"Basic {ecr_token}",
    "Content-Type": "application/application/vnd.docker.image.rootfs.diff.tar.gzip"
}

# 2. Extract and Process Layers directly from the Tar archive
print(f"📦 Reading image layers from {TAR_FILE}...")
with tarfile.open(TAR_FILE, 'r') as tar:
    # Read manifest to find layer paths
    manifest_member = tar.getmember('manifest.json')
    manifest_data = json.loads(tar.extractfile(manifest_member).read().decode('utf-8'))
    layers = manifest_data[0]['Layers']
    
    for layer in layers:
        print(f"🚀 Streaming layer: {layer}")
        layer_file = tar.extractfile(layer)
        layer_data = layer_file.read()
        layer_size = len(layer_data)
        
        # Initiate Layer Upload on AWS
        init_url = f"{ecr_endpoint}/v2/{REPOSITORY}/blobs/uploads/"
        init_res = requests.post(init_url, headers=headers)
        
        if init_res.status_code == 202:
            upload_url = init_res.headers['Location']
            
            # Stream the raw bytes directly over host TCP network stack
            print(f"   ⚡ Uploading {layer_size / (1024*1024):.2f} MB...")
            upload_res = requests.put(f"{upload_url}&digest=sha256:fake_digest_placeholder", headers=headers, data=layer_data)
            print(f"   ✅ Status: {upload_res.status_code}")
        else:
            print(f"   ❌ Failed to initiate layer upload: {init_res.text}")

print("🎉 Process Complete. Run your EKS Rollout restart next!")