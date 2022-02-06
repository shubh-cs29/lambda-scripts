import json
import boto3
import smtplib
import email.message

cf_client = boto3.client("cloudformation")
paginator = cf_client.get_paginator('list_stacks')
marker = None
stack_name_list = []
stack_status_list = []

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
            stack_name_list.append(stack['StackName'])
            stack_status_list.append(stack['StackStatus'])
            
    stack_name_list_string = '\n'.join(stack_name_list)
    stack_status_list_string = '\n'.join(stack_status_list)
    
    sender = "<SENDER_EMAIL>"
    receiver = "<RECEIVER_EMAIL>"
    password = "<GMAIL_APP_PASSWORD>"
    host = "smtp.gmail.com"
    port = "587"

    html = """
    <html>
        <style>
          table, th, td {{ border: 1px solid black; border-collapse: collapse; }}
          th, td {{ padding: 1px; }}
        </style>
        <body>
          <table style="border: 1px solid #990000; border-collapse: collapse">
             <tr style="border: 1px solid #990000; border-collapse: collapse">
              <th style="border: 1px solid #990000; border-collapse: collapse">Stack Name</th>
              <th style="border: 1px solid #990000; border-collapse: collapse">Stack Status</th>
             </tr>
             <tr style="border: 1px solid #990000; border-collapse: collapse">
              <td style="border: 1px solid #990000; border-collapse: collapse; white-space:pre">{stack_name_list_string}</td>
              <td style="border: 1px solid #990000; border-collapse: collapse; white-space:pre">{stack_status_list_string}</td>
             </tr>
          </table>
        </body>
    </html>
    """.format(stack_name_list_string=stack_name_list_string, stack_status_list_string=stack_status_list_string)
    
    msg = email.message.Message()
    msg['Subject'] = "List All CF Stacks"
    msg['From'] = sender
    msg['To'] = receiver
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(html)
    try:
        server = smtplib.SMTP(host, port)
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.close()
        return True
    except Exception as ex:
        print (ex)
        return False
