import json, boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

model_id = "arn:aws:bedrock:us-east-1:730335308061:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0"
payload = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 512,
    "messages": [
        {"role": "user", "content": [{"type": "text", "text": "Hello, Claude!"}]}
    ],
}

resp = client.invoke_model(
    modelId=model_id,
    contentType="application/json",
    accept="application/json",
    body=json.dumps(payload).encode("utf-8"),
)
data = json.loads(resp["body"].read())

print(data.get("content", [{}])[0].get("text") or json.dumps(data, indent=2))
