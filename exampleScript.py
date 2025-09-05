import json, boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

model_id = "arn:aws:bedrock:us-east-1:730335308061:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0"
payload = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 512,
    "messages": [
        {"role": "user", "content": [
            {"type": "text", "text": "It works on my skin type"},
            {"type": "text", "text": "I'm not sure."},
            {"type": "text", "text": "I buy what I can to make My girlfriend or wife smell good"},
            {"type": "text", "text": "The brand of the product itself"},
            {"type": "text", "text": "These products stand out because they're high-quality and look prefect on my skin."},
            {"type": "text", "text": "the smell on me"},
            {"type": "text", "text": "it seems like it was made just for me"},
            {"type": "text", "text": "They will be nuce"},
            {"type": "text", "text": "From the input above, can you give me a theme for the responses?"},
            ]}
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
