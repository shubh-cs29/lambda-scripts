import json
import boto3

ec2 = boto3.resource('ec2', region_name='ap-southeast-1')
sns = boto3.client('sns', region_name='ap-southeast-1')

def lambda_handler():
    lst = []
    subnets = ec2.subnets.all()
    result = ""
    
    for subnet in list(subnets):
        free_ips = subnet.available_ip_address_count
        n = int(subnet.cidr_block.split('/')[1])
        cidr_ips = 2**(32-n)
        used_ips = cidr_ips - free_ips
        ip_stats = '{:s}: cidr={:d}, aws used=5, you used={:d}, free={:d}'.\
        format(subnet.id, cidr_ips, used_ips - 5, free_ips)
        result += ip_stats+"\n"
        print(var)

    if free_ips < 10:
        sns_response = sns.publish(
        TopicArn='<SNS_TOPC_ARN>',
        Message=result,
        Subject='IP ALERT....'
        )

lambda_handler()
