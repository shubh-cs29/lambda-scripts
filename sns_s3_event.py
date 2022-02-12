import json
import boto3

sns_client = boto3.client('sns')
s3_dictionary = {}
sns_topic_arn = '<SNS_TOPIC_ARN>'

def lambda_handler(event, context):
    bucket_name = event['detail']['requestParameters']['bucketName']
    bucket_owner = event['detail']['userIdentity']['arn']
    s3_dictionary.update({"BUCKET NAME": bucket_name, "BUCKET OWNER" :bucket_owner})
    sns_client.publish(
        TopicArn = sns_topic_arn,
        Subject = 'S3 Bucket Created',
        Message = json.dumps({'default': json.dumps(s3_dictionary, sort_keys=False, indent=4)}),
        MessageStructure='json'
    )

