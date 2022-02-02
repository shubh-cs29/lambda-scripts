import json
import boto3
import smtplib
import email.message

cf_client = boto3.client('cloudformation')
deleted_stacks_list = []

def lambda_handler(event, context):
    marker = None
    global counter
    paginator = cf_client.get_paginator('list_stacks')
    response_iterator = paginator.paginate(
      StackStatusFilter=["DELETE_COMPLETE"],
      PaginationConfig={'StartingToken': marker})
    for page in response_iterator:
      for stack_name in page['StackSummaries']:
        deleted_stacks_list.append(stack_name['StackName'])
    deleted_stacks_list_string = '\n'.join(deleted_stacks_list)
    print(deleted_stacks_list_string)
    
    sender = "<SENDER_EMAIL>"
    receiver = "<RECEIVER_EMAIL>"
    password = "<APP_PASSWORD>" # go to gmail settings and create App Password
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
              <th style="border: 1px solid #990000; border-collapse: collapse">Deleted Stacks</th>
             </tr>
             <tr style="border: 1px solid #990000; border-collapse: collapse">
              <td style="border: 1px solid #990000; border-collapse: collapse">{deleted_stacks_list_string}</td>
             </tr>
          </table>
        </body>
    </html>
    """.format(deleted_stacks_list_string=deleted_stacks_list_string)
    
    msg = email.message.Message()
    msg['Subject'] = "Deleted CF Stacks"
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

