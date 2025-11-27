import boto3
import sagemaker
import os
import time
from sagemaker.pytorch.model import PyTorchModel

# AWS configuration
AWS_REGION = "us-east-1"  # Change to your preferred region
# TODO: Update this role ARN with the correct one for your account
ROLE_ARN = "arn:aws:iam::083636777260:role/pilih-frame-compute-role" 
MODEL_NAME = "car-detection-model"
ENDPOINT_NAME = "car-detection-endpoint"

def deploy_model():
    """Deploy car detection model to SageMaker"""

    # Initialize SageMaker session
    boto_session = boto3.Session(region_name=AWS_REGION)
    sagemaker_session = sagemaker.Session(boto_session)
    
    # Check if endpoint already exists
    sagemaker_client = boto_session.client("sagemaker")
    try:
        sagemaker_client.describe_endpoint(EndpointName=ENDPOINT_NAME)
        print(f"Endpoint {ENDPOINT_NAME} already exists. Skipping deployment.")
        return None
    except sagemaker_client.exceptions.ClientError:
        pass # Endpoint does not exist, proceed

    # Determine the absolute path to the directory containing this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "model.tar.gz")

    print("Uploading model to S3...")
    # Upload model.tar.gz to default bucket
    # Ensure model.tar.gz exists
    if not os.path.exists(model_path):
        # Create a dummy model.tar.gz if it doesn't exist (for testing purposes if needed, 
        # but ideally it should be there from the repo)
        # For now, we assume it exists as seen in the file list
        raise FileNotFoundError(f"model.tar.gz not found at {model_path}")

    model_data = sagemaker_session.upload_data(
        path=model_path,
        key_prefix="car-detection-model"
    )
    print(f"Model uploaded to: {model_data}")

    # Create model (using PyTorch container for simplicity)
    model = PyTorchModel(
        name=MODEL_NAME,
        model_data=model_data,
        role=ROLE_ARN,
        entry_point="inference.py",
        source_dir=base_dir, # Use absolute path
        framework_version="1.12",
        py_version="py38",
        sagemaker_session=sagemaker_session,
    )

    print(f"Deploying model to endpoint: {ENDPOINT_NAME}...")
    # Deploy to endpoint
    predictor = model.deploy(
        initial_instance_count=1,
        instance_type="ml.t2.medium",
        endpoint_name=ENDPOINT_NAME,
    )

    print(f"Model deployed successfully to endpoint: {ENDPOINT_NAME}")
    return predictor


if __name__ == "__main__":
    deploy_model()
