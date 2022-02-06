import json
import boto3
import smtplib
import email.message

# cloudwatch event rule for create RDS Instance event
"""
{
  "source": [
    "aws.rds"
  ],
  "detail-type": [
    "AWS API Call via CloudTrail"
  ],
  "detail": {
    "eventSource": [
      "rds.amazonaws.com"
    ],
    "eventName": [
      "CreateDBInstance"
    ]
  }
}
"""

def lambda_handler(event, context):
    rds_instance_name = event['detail']['requestParameters']['dBInstanceIdentifier']
    
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
              <th style="border: 1px solid #990000; border-collapse: collapse">RDS Instance</th>
             </tr>
             <tr style="border: 1px solid #990000; border-collapse: collapse">
              <td style="border: 1px solid #990000; border-collapse: collapse; white-space:pre">{rds_instance_name}</td>
             </tr>
          </table>
        </body>
    </html>
    """.format(rds_instance_name=rds_instance_name)
    
    msg = email.message.Message()
    msg['Subject'] = "New RDS Instance Created"
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
