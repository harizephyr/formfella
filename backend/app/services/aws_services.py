import boto3
import json

class AWSServiceManager:
    def __init__(self):
        self.session = boto3

    def s3(self):
        return self.session.client('s3')

    def sqs(self):
        return self.session.client('sqs')

    def bedrock_runtime(self):
        return self.session.client('bedrock-runtime')

    def lambda_(self):
        return self.session.client('lambda')

    def secrets_manager(self):
        return self.session.client('secretsmanager')

    def dynamodb(self):
        return self.session.resource('dynamodb')

    def textract(self):
        return self.session.client('textract')

    def redshift(self):
        return self.session.client('redshift')

    def kendra(self):
        return self.session.client('kendra')

    def sagemaker(self):
        return self.session.client('sagemaker')

    def cloudwatch_logs(self):
        return self.session.client('logs')

    # Example: Retrieve a secret value
    def get_secret(self, secret_name):
        client = self.secrets_manager()
        response = client.get_secret_value(SecretId=secret_name)
        return response.get('SecretString')

    # Example: Get S3 object
    def get_s3_object(self, bucket, key):
        s3 = self.s3()
        return s3.get_object(Bucket=bucket, Key=key)['Body'].read()

    # Example: Send SQS message
    def send_sqs_message(self, queue_url, message_body):
        sqs = self.sqs()
        return sqs.send_message(QueueUrl=queue_url, MessageBody=message_body)

    # Example: Invoke Lambda function
    def invoke_lambda(self, function_name, payload):
        lambda_client = self.lambda_()
        return lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=payload
        )


# Services Usage
def init_aws():
    aws = AWSServiceManager()
    return aws

def get_secret(secret_name="formfella-env"):
    client = init_aws().secrets_manager()
    
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            # Parse the JSON string to a dictionary
            return json.loads(secret)
        else:
            # Handle binary secrets (unlikely for .env content)
            return get_secret_value_response['SecretBinary']

# print(get_secret())