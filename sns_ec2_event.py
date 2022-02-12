import json
import boto3

sns_client = boto3.client('sns')
ec2_dictionary = {}
sns_topic_arn = '<SNS_TOPIC_ARN>'

def lambda_handler(event, context):
    instance_id = event['detail']['responseElements']['instancesSet']['items'][0]['instanceId']
    instance_owner = event['detail']['userIdentity']['arn']
    ec2_dictionary.update({"EC2 ID": instance_id, "EC2 OWNER" :instance_owner})
    sns_client.publish(
        TopicArn = sns_topic_arn,
        Subject = 'EC2 Instance Created',
        Message = json.dumps({'default': json.dumps(ec2_dictionary, sort_keys=False, indent=4)}),
        MessageStructure='json'
    )

