import json
import boto3

sns_client = boto3.client('sns')
rds_dictionary = {}
sns_topic_arn = '<SNS_TOPIC_ARN>'

def lambda_handler(event, context):
    rds_instance_name = event['detail']['requestParameters']['dBInstanceIdentifier']
    rds_instance_owner = event['detail']['userIdentity']['arn']
    rds_dictionary.update({"DB NAME": rds_instance_name, "DB OWNER" :rds_instance_owner})
    sns_client.publish(
        TopicArn = sns_topic_arn,
        Subject = 'RDS Instance Created',
        Message = json.dumps({'default': json.dumps(rds_dictionary, sort_keys=False, indent=4)}),
        MessageStructure='json'
    )
    
