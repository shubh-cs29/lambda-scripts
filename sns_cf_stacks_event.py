import json
import boto3

cf_client = boto3.client("cloudformation")
paginator = cf_client.get_paginator('list_stacks')
sns_client = boto3.client('sns')
marker = None
stack_dictionary = {}
sns_topic_arn = '<SNS_TOPIC_ARN>'

def lambda_handler(event, context):
    response_iterator = paginator.paginate(
        StackStatusFilter=[
            'CREATE_IN_PROGRESS','CREATE_FAILED','CREATE_COMPLETE','ROLLBACK_IN_PROGRESS','ROLLBACK_FAILED','ROLLBACK_COMPLETE','DELETE_IN_PROGRESS','DELETE_FAILED','DELETE_COMPLETE','UPDATE_IN_PROGRESS','UPDATE_COMPLETE_CLEANUP_IN_PROGRESS','UPDATE_COMPLETE','UPDATE_FAILED','UPDATE_ROLLBACK_IN_PROGRESS','UPDATE_ROLLBACK_FAILED','UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS','UPDATE_ROLLBACK_COMPLETE','REVIEW_IN_PROGRESS','IMPORT_IN_PROGRESS','IMPORT_COMPLETE','IMPORT_ROLLBACK_IN_PROGRESS','IMPORT_ROLLBACK_FAILED','IMPORT_ROLLBACK_COMPLETE'
        ],
    PaginationConfig={
      'StartingToken': marker})  
      
    for page in response_iterator:
        stack_summaries = page['StackSummaries']
        for stack in stack_summaries:
            stack_dictionary.update({stack['StackName']:stack['StackStatus']})
          
    sns_client.publish(
        TopicArn = sns_topic_arn,
        Subject = 'CF Stacks',
        Message=json.dumps({'default': json.dumps(stack_dictionary, sort_keys=False, indent=4)}),
        MessageStructure='json'
    )

