import boto3
import sys

# AWS configuration
AWS_REGION = "us-east-1"
ENDPOINT_NAME = "car-detection-endpoint"
ENDPOINT_CONFIG_NAME = "car-detection-endpoint-config" # Usually created by SageMaker with a similar name, but we might need to look it up or just try to delete the endpoint which usually leaves the config.
# Actually, model.deploy creates an endpoint config with the same name as the endpoint usually, or auto-generated.
# Best practice is to describe the endpoint to get the config name.

def delete_endpoint():
    """Delete SageMaker endpoint and configuration"""
    session = boto3.Session(region_name=AWS_REGION)
    sagemaker_client = session.client("sagemaker")

    print(f"Attempting to delete endpoint: {ENDPOINT_NAME}")
    
    # 1. Get Endpoint Config Name
    try:
        response = sagemaker_client.describe_endpoint(EndpointName=ENDPOINT_NAME)
        config_name = response['EndpointConfigName']
    except sagemaker_client.exceptions.ClientError as e:
        if "Could not find endpoint" in str(e):
            print(f"Endpoint {ENDPOINT_NAME} not found.")
            config_name = None
        else:
            print(f"Error describing endpoint: {e}")
            return

    # 2. Delete Endpoint
    if config_name:
        try:
            sagemaker_client.delete_endpoint(EndpointName=ENDPOINT_NAME)
            print(f"Endpoint {ENDPOINT_NAME} deletion initiated.")
        except Exception as e:
            print(f"Error deleting endpoint: {e}")

        # 3. Delete Endpoint Config
        print(f"Attempting to delete endpoint config: {config_name}")
        try:
            sagemaker_client.delete_endpoint_config(EndpointConfigName=config_name)
            print(f"Endpoint config {config_name} deleted.")
        except Exception as e:
            print(f"Error deleting endpoint config: {e}")
    
    print("Cleanup complete.")

if __name__ == "__main__":
    # Confirmation prompt
    confirm = input(f"Are you sure you want to delete endpoint '{ENDPOINT_NAME}'? (y/n): ")
    if confirm.lower() == 'y':
        delete_endpoint()
    else:
        print("Deletion cancelled.")
