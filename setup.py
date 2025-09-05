#!/usr/bin/env python3
"""
Setup script for Smart Text Analytics Pipeline
AWS Engineering Day Hackathon

This script helps set up the environment and test AWS connectivity.
"""

import os
import sys
import subprocess
import json
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True


def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def test_aws_credentials():
    """Test AWS credentials and profile"""
    print("\n🔑 Testing AWS credentials...")

    # Check if AWS profile is set
    aws_profile = os.environ.get('AWS_PROFILE', 'platform-test-engineering-day')
    print(f"Using AWS Profile: {aws_profile}")

    try:
        session = boto3.Session(profile_name=aws_profile)
        sts = session.client('sts')

        # Test credentials
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials valid")
        print(f"   Account: {identity.get('Account', 'Unknown')}")
        print(f"   User/Role: {identity.get('Arn', 'Unknown').split('/')[-1]}")

        return True

    except NoCredentialsError:
        print("❌ AWS credentials not found")
        print("   Please configure AWS SSO or credentials")
        return False
    except ClientError as e:
        print(f"❌ AWS credentials error: {e}")
        return False


def test_aws_services():
    """Test access to required AWS services"""
    print("\n🧪 Testing AWS service access...")

    aws_profile = os.environ.get('AWS_PROFILE', 'platform-test-engineering-day')
    session = boto3.Session(profile_name=aws_profile)

    services_status = {}

    # Test Comprehend
    try:
        comprehend = session.client('comprehend', region_name='us-east-1')
        comprehend.detect_sentiment(Text="Test message", LanguageCode='en')
        services_status['comprehend'] = True
        print("✅ Amazon Comprehend access confirmed")
    except Exception as e:
        services_status['comprehend'] = False
        print(f"❌ Amazon Comprehend access failed: {str(e)[:100]}...")

    # Test Bedrock
    try:
        bedrock = session.client('bedrock-runtime', region_name='us-east-1')

        # Test Titan embeddings
        payload = {"inputText": "test", "dimensions": 512, "normalize": True}
        bedrock.invoke_model(
            modelId="arn:aws:bedrock:us-east-1:730335308061:inference-profile/us.amazon.titan-text-embed-v2:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )
        services_status['bedrock_titan'] = True
        print("✅ Bedrock Titan Embeddings access confirmed")

        # Test Claude
        claude_payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": [{"type": "text", "text": "Hi"}]}]
        }
        bedrock.invoke_model(
            modelId="arn:aws:bedrock:us-east-1:730335308061:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(claude_payload)
        )
        services_status['bedrock_claude'] = True
        print("✅ Bedrock Claude access confirmed")

    except Exception as e:
        services_status['bedrock_titan'] = False
        services_status['bedrock_claude'] = False
        print(f"❌ Bedrock access failed: {str(e)[:100]}...")

    return services_status


def check_sample_data():
    """Check if sample data files exist"""
    print("\n📄 Checking sample data...")

    sample_dir = "sample_data"
    if not os.path.exists(sample_dir):
        print(f"❌ Sample data directory '{sample_dir}' not found")
        return False

    sample_files = [f"data_set_{i}.csv" for i in range(1, 7)]
    missing_files = []

    for filename in sample_files:
        filepath = os.path.join(sample_dir, filename)
        if os.path.exists(filepath):
            print(f"✅ {filename} found")
        else:
            missing_files.append(filename)
            print(f"❌ {filename} not found")

    if missing_files:
        print(f"❌ Missing {len(missing_files)} sample data files")
        return False

    print("✅ All sample data files found")
    return True


def main():
    """Main setup function"""
    print("🚀 Smart Text Analytics Pipeline Setup")
    print("=" * 50)

    success = True

    # Check Python version
    if not check_python_version():
        success = False

    # Install dependencies
    if not install_dependencies():
        success = False

    # Test AWS credentials
    if not test_aws_credentials():
        success = False

    # Test AWS services (optional - may fail in some environments)
    services_status = test_aws_services()

    # Check sample data
    if not check_sample_data():
        success = False

    print("\n" + "=" * 50)

    if success and all(services_status.values()):
        print("🎉 Setup completed successfully!")
        print("   You can now run: python smart_analytics_pipeline.py")
    elif success:
        print("⚠️  Setup mostly successful with some service access issues")
        print("   The pipeline may still work, but some features might be limited")
        print("   You can try running: python smart_analytics_pipeline.py")
    else:
        print("❌ Setup failed. Please fix the issues above before proceeding.")
        return 1

    print("\n📋 Next steps:")
    print("   1. Run the pipeline: python smart_analytics_pipeline.py")
    print("   2. Check the output JSON files for results")
    print("   3. Modify the pipeline as needed for your use case")

    return 0


if __name__ == "__main__":
    exit(main())
