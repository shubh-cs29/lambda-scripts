import json
import boto3
import smtplib
import email.message

# event rule trigger
"""
{
  "detail-type": [
    "AWS API Call via CloudTrail"
  ],
  "source": [
    "aws.ec2"
  ],
  "detail": {
    "eventSource": [
      "ec2.amazonaws.com"
    ],
    "eventName": [
      "RunInstances"
    ]
  }
}

"""

def lambda_handler(event, context):
    instance_type = event['detail']['requestParameters']['instanceType']
    instance_id = event['detail']['responseElements']['instancesSet']['items'][0]['instanceId']
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
               <th style="border: 1px solid #990000; border-collapse: collapse">Instance ID</th>
               <th style="border: 1px solid #990000; border-collapse: collapse">Instance Type</th>
             </tr>
             <tr style="border: 1px solid #990000; border-collapse: collapse">
               <td style="border: 1px solid #990000; border-collapse: collapse" >{instance_id}</td>
               <td style="border: 1px solid #990000; border-collapse: collapse">{instance_type}</td>
             </tr>
           </table>
        </body>
    </html>
    """.format(instance_id=instance_id, instance_type=instance_type)
    
    msg = email.message.Message()
    msg['Subject'] = "New EC2 Instance"
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

