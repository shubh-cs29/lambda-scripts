import boto3

# Define the AWS region primary and secondary
primary_region = 'us-east-1'
secondary_region = 'us-east-2'

account_id = boto3.client("sts").get_caller_identity()["Account"]

# Define the tags to check for
tags_to_check = [
    {'Key': 'ApplicationCI', 'Value': 'adh'},
    {'Key': 'ApplicationCI', 'Value': 'bbs'},
    {'Key': 'ApplicationCI', 'Value': 'bju'}
]


# Define the tag to add if the criteria are met
primary_tag = {'Key': 'primay', 'Value': 'yes'}
secondary_tag = {'Key': 'primay', 'Value': 'no'}


def primary_dynamodb_tagging():
    # Create a Boto3 DynamoDB client for the specified region
    dynamodb = boto3.client('dynamodb', region_name=primary_region)

    try:
        # List all tables in the DynamoDB instance
        response = dynamodb.list_tables()
        
        # Check if the 'TableNames' key exists in the response
        if 'TableNames' in response:
            print(f"DynamoDB tables in primary region '{primary_region}':")
            for table_name in response['TableNames']:
                response = dynamodb.list_tags_of_resource(ResourceArn=f'arn:aws:dynamodb:{primary_region}:{account_id}:table/{table_name}')
                if any(tag in response['Tags'] for tag in tags_to_check):
                  dynamodb.tag_resource(ResourceArn=f'arn:aws:dynamodb:{primary_region}:{account_id}:table/{table_name}', Tags=[primary_tag])
                  print(f"Added tag '{primary_tag['Key']}={primary_tag['Value']}' to DynamoDB table '{table_name}' in primary region '{primary_region}'.")
                else:
                  print(f"The required tags are not present on DynamoDB table '{table_name}' in primary region '{primary_region}'.")

        else:
            print(f"No DynamoDB tables found in primary region '{primary_region}'.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")



def primary_ec2_tagging():
    ec2 = boto3.client('ec2', region_name=primary_region)
    instances = ec2.describe_instances()

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            # Check if any of the specified tags exist on the instance
            tags = instance.get('Tags', [])
            print(tags)
            if any(tag in tags for tag in tags_to_check):
                # Add the 'primary=yes' tag to the instance
              ec2.create_tags(Resources=[instance_id], Tags=[primary_tag])
              print(f"Tagged instance {instance_id} with 'primary=yes'")
            else:
              print(f"The required tags are not present on EC2 instance '{instance_id}' in primary region '{primary_region}'.")



def primary_elb_tagging():
    elb_client = boto3.client('elbv2', region_name=primary_region)  # Use the region you want to target

    elbs = elb_client.describe_load_balancers()

    for elb in elbs['LoadBalancers']:
        elb_arn = elb['LoadBalancerArn']
        # Describe the tags for the current ELB
        elb_tags = elb_client.describe_tags(ResourceArns=[elb_arn])
        # Check if any of the specified tags exist
        if any(tag in elb_tags['TagDescriptions'][0]['Tags'] for tag in tags_to_check):
            elb_client.add_tags(
                ResourceArns=[elb_arn],
                Tags=[primary_tag]
            )
            print(f"Tagged ELB {elb['LoadBalancerName']} with 'primary=yes'")
        else:
            print(f"The required tags are not present on ELB '{elb['LoadBalancerName']}' in primary region '{primary_region}'.")


def primary_autoscaling_tagging():
    list_of_dicts = []
    autoscaling_client = boto3.client('autoscaling', region_name=primary_region)
    # Describe all Auto Scaling groups in your AWS account
    response = autoscaling_client.describe_auto_scaling_groups()

    for group in response['AutoScalingGroups']:
        # Check if any of the specified tags exist on the Auto Scaling group
        existing_tags = group.get('Tags', [])
        #print(existing_tags)
        for kv in existing_tags:
          kv_dict = {'Key': kv['Key'], 'Value': kv['Value']}
          list_of_dicts.append(kv_dict)

        tag_exists = any(tag in list_of_dicts for tag in tags_to_check)
        # If any of the specified tags exist, add the 'primary=yes' tag
        if tag_exists:
            autoscaling_client.create_or_update_tags(
                Tags=[
                    {
                        'ResourceId': group['AutoScalingGroupName'],
                        'ResourceType': 'auto-scaling-group',
                        'Key': 'primary',
                        'Value': 'yes',
                        'PropagateAtLaunch': True
                    }
                ]
            )
            print(f"Tag 'primary=yes' added to Auto Scaling group '{group['AutoScalingGroupName']}'.")
        else:
            print(f"None of the specified tags exist on Auto Scaling group '{group['AutoScalingGroupName']}'.")


def primary_eks_tagging():
    # Initialize the EKS client
    eks_client = boto3.client('eks', region_name=primary_region)

    tags_to_check = [
        {'key': 'ApplicationCI', 'value': 'adh'},
        {'key': 'ApplicationCI', 'value': 'bbs'},
        {'key': 'ApplicationCI', 'value': 'bju'}
    ]

    # List your EKS clusters
    clusters = eks_client.list_clusters()
    cluster_names = clusters['clusters']
    for cluster_name in cluster_names:
        # Describe the cluster to get its tags
        cluster_info = eks_client.describe_cluster(name=cluster_name)
        cluster_tags = cluster_info['cluster']['tags']
        list_of_dics = [{'key': key, 'value': value} for key, value in cluster_tags.items()]
    
        # Check if any of the specified tags exist on the cluster
        if any(tag in list_of_dics for tag in tags_to_check):
                # If a matching tag is found, tag the cluster with "primary=yes"
                eks_client.tag_resource(resourceArn=cluster_info['cluster']['arn'], tags={'primary' : 'yes'})
                print(f"Tagged cluster {cluster_name} with 'primary=yes'")
                
        else:
            print(f"The required tags are not present on EKS Cluster '{cluster_name}' in primary region '{primary_region}'.")


def primary_target_group_tagging():
    # Initialize the Boto3 ELB client
    elbv2_client = boto3.client('elbv2', region_name=primary_region)

    # Get a list of all target groups
    response = elbv2_client.describe_target_groups()

    # Loop through the target groups
    for target_group in response['TargetGroups']:
        # Get the ARN of the target group
        target_group_arn = target_group['TargetGroupArn']
        
        # Get the current tags for the target group
        current_tags = elbv2_client.describe_tags(ResourceArns=[target_group_arn])['TagDescriptions'][0]['Tags']
        
        # Check if any of the specified tags exist on the target group
        if any(tag in current_tags for tag in tags_to_check):
            # If any of the specified tags exist, add the 'primary=yes' tag
            elbv2_client.add_tags(ResourceArns=[target_group_arn], Tags=[primary_tag])
            print(f"Added 'primary=yes' tag to target group {target_group['TargetGroupName']}")
        else:
            print(f"The required tags are not present on target group {target_group['TargetGroupName']} in primary region '{primary_region}'.")


def primary_launch_template_tagging():
    ec2_client = boto3.client('ec2', region_name=primary_region)

    # Get a list of all launch templates
    response = ec2_client.describe_launch_templates()

    # Loop through the launch templates
    for launch_template in response['LaunchTemplates']:
        # Get the ID of the launch template
        launch_template_id = launch_template['LaunchTemplateId']
        
        # Get the current tags for the launch template
        current_tags = ec2_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [launch_template_id]}])['Tags']
        current_tags = [{'Key': item['Key'], 'Value': item['Value']} for item in current_tags]

        # Check if any of the specified tags exist on the launch template
        if any(tag in current_tags for tag in tags_to_check):
            # If any of the specified tags exist, add the 'primary=yes' tag
            ec2_client.create_tags(Resources=[launch_template_id], Tags=[primary_tag])
            print(f"Added 'primary=yes' tag to launch template {launch_template_id}")
        else:
            print(f"The required tags are not present on launch template {launch_template_id} in primary region '{primary_region}'.")





def secondary_dynamodb_tagging():
    # Create a Boto3 DynamoDB client for the specified region
    dynamodb = boto3.client('dynamodb', region_name=secondary_region)

    try:
        # List all tables in the DynamoDB instance
        response = dynamodb.list_tables()
        
        # Check if the 'TableNames' key exists in the response
        if 'TableNames' in response:
            print(f"DynamoDB tables in secondary region '{secondary_region}':")
            for table_name in response['TableNames']:
                response = dynamodb.list_tags_of_resource(ResourceArn=f'arn:aws:dynamodb:{secondary_region}:{account_id}:table/{table_name}')
                if any(tag in response['Tags'] for tag in tags_to_check):
                  dynamodb.tag_resource(ResourceArn=f'arn:aws:dynamodb:{secondary_region}:{account_id}:table/{table_name}', Tags=[secondary_tag])
                  print(f"Added tag '{secondary_tag['Key']}={secondary_tag['Value']}' to DynamoDB table '{table_name}' in secondary region '{secondary_region}'.")
                else:
                  print(f"The required tags are not present on DynamoDB table '{table_name}' in secondary region '{secondary_region}'.")

        else:
            print(f"No DynamoDB tables found in secondary region '{secondary_region}'.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")



def secondary_ec2_tagging():
    ec2 = boto3.client('ec2', region_name=secondary_region)
    instances = ec2.describe_instances()

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            # Check if any of the specified tags exist on the instance
            tags = instance.get('Tags', [])
            print(tags)
            if any(tag in tags for tag in tags_to_check):
                # Add the 'primary=no' tag to the instance
              ec2.create_tags(Resources=[instance_id], Tags=[secondary_tag])
              print(f"Tagged instance {instance_id} with 'primary=no'")
            else:
              print(f"The required tags are not present on EC2 instance '{instance_id}' in secondary region '{secondary_region}'.")



def secondary_elb_tagging():
    elb_client = boto3.client('elbv2', region_name=secondary_region)  # Use the region you want to target

    elbs = elb_client.describe_load_balancers()

    for elb in elbs['LoadBalancers']:
        elb_arn = elb['LoadBalancerArn']
        # Describe the tags for the current ELB
        elb_tags = elb_client.describe_tags(ResourceArns=[elb_arn])
        # Check if any of the specified tags exist
        if any(tag in elb_tags['TagDescriptions'][0]['Tags'] for tag in tags_to_check):
            elb_client.add_tags(
                ResourceArns=[elb_arn],
                Tags=[secondary_tag]
            )
            print(f"Tagged ELB {elb['LoadBalancerName']} with 'primary=no'")
        else:
            print(f"The required tags are not present on ELB '{elb['LoadBalancerName']}' in secondary region '{secondary_region}'.")


def secondary_autoscaling_tagging():
    list_of_dicts = []
    autoscaling_client = boto3.client('autoscaling', region_name=secondary_region)
    # Describe all Auto Scaling groups in your AWS account
    response = autoscaling_client.describe_auto_scaling_groups()

    for group in response['AutoScalingGroups']:
        # Check if any of the specified tags exist on the Auto Scaling group
        existing_tags = group.get('Tags', [])
        #print(existing_tags)
        for kv in existing_tags:
          kv_dict = {'Key': kv['Key'], 'Value': kv['Value']}
          list_of_dicts.append(kv_dict)

        tag_exists = any(tag in list_of_dicts for tag in tags_to_check)
        # If any of the specified tags exist, add the 'primary=no' tag
        if tag_exists:
            autoscaling_client.create_or_update_tags(
                Tags=[
                    {
                        'ResourceId': group['AutoScalingGroupName'],
                        'ResourceType': 'auto-scaling-group',
                        'Key': 'primary',
                        'Value': 'no',
                        'PropagateAtLaunch': True
                    }
                ]
            )
            print(f"Tag 'primary=no' added to Auto Scaling group '{group['AutoScalingGroupName']}'.")
        else:
            print(f"None of the specified tags exist on Auto Scaling group '{group['AutoScalingGroupName']}'.")


def secondary_eks_tagging():
    # Initialize the EKS client
    eks_client = boto3.client('eks', region_name=secondary_region)

    tags_to_check = [
        {'key': 'ApplicationCI', 'value': 'adh'},
        {'key': 'ApplicationCI', 'value': 'bbs'},
        {'key': 'ApplicationCI', 'value': 'bju'}
    ]

    # List your EKS clusters
    clusters = eks_client.list_clusters()
    cluster_names = clusters['clusters']
    for cluster_name in cluster_names:
        # Describe the cluster to get its tags
        cluster_info = eks_client.describe_cluster(name=cluster_name)
        cluster_tags = cluster_info['cluster']['tags']
        list_of_dics = [{'key': key, 'value': value} for key, value in cluster_tags.items()]
    
        # Check if any of the specified tags exist on the cluster
        if any(tag in list_of_dics for tag in tags_to_check):
                # If a matching tag is found, tag the cluster with "primary=no"
                eks_client.tag_resource(resourceArn=cluster_info['cluster']['arn'], tags={'primary' : 'no'})
                print(f"Tagged cluster {cluster_name} with 'primary=no'")
                
        else:
            print(f"The required tags are not present on EKS Cluster '{cluster_name}' in secondary region '{secondary_region}'.")


def secondary_target_group_tagging():
    # Initialize the Boto3 ELB client
    elbv2_client = boto3.client('elbv2', region_name=secondary_region)

    # Get a list of all target groups
    response = elbv2_client.describe_target_groups()

    # Loop through the target groups
    for target_group in response['TargetGroups']:
        # Get the ARN of the target group
        target_group_arn = target_group['TargetGroupArn']
        
        # Get the current tags for the target group
        current_tags = elbv2_client.describe_tags(ResourceArns=[target_group_arn])['TagDescriptions'][0]['Tags']
        
        # Check if any of the specified tags exist on the target group
        if any(tag in current_tags for tag in tags_to_check):
            # If any of the specified tags exist, add the 'primary=no' tag
            elbv2_client.add_tags(ResourceArns=[target_group_arn], Tags=[secondary_tag])
            print(f"Added 'primary=no' tag to target group {target_group['TargetGroupName']}")
        else:
            print(f"The required tags are not present on target group {target_group['TargetGroupName']} in secondary region '{secondary_region}'.")


def secondary_launch_template_tagging():
    ec2_client = boto3.client('ec2', region_name=secondary_region)

    # Get a list of all launch templates
    response = ec2_client.describe_launch_templates()

    # Loop through the launch templates
    for launch_template in response['LaunchTemplates']:
        # Get the ID of the launch template
        launch_template_id = launch_template['LaunchTemplateId']
        
        # Get the current tags for the launch template
        current_tags = ec2_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [launch_template_id]}])['Tags']
        current_tags = [{'Key': item['Key'], 'Value': item['Value']} for item in current_tags]

        # Check if any of the specified tags exist on the launch template
        if any(tag in current_tags for tag in tags_to_check):
            # If any of the specified tags exist, add the 'primary=no' tag
            ec2_client.create_tags(Resources=[launch_template_id], Tags=[secondary_tag])
            print(f"Added 'primary=no' tag to launch template {launch_template_id}")
        else:
            print(f"The required tags are not present on launch template {launch_template_id} in secondary region '{secondary_region}'.")


# def lambda_handler(event, context):
#     primary_dynamodb_tagging()
#     primary_ec2_tagging()
#     primary_elb_tagging()
#     primary_autoscaling_tagging()
#     primary_eks_tagging()
#     primary_target_group_tagging()
#     primary_launch_template_tagging()

#     secondary_dynamodb_tagging()
#     secondary_ec2_tagging()
#     secondary_elb_tagging()
#     secondary_autoscaling_tagging()
#     secondary_eks_tagging()
#     secondary_target_group_tagging()
#     secondary_launch_template_tagging()

if __name__ == "__main__":
    primary_dynamodb_tagging()
    primary_ec2_tagging()
    primary_elb_tagging()
    primary_autoscaling_tagging()
    primary_eks_tagging()
    primary_target_group_tagging()
    primary_launch_template_tagging()

    secondary_dynamodb_tagging()
    secondary_ec2_tagging()
    secondary_elb_tagging()
    secondary_autoscaling_tagging()
    secondary_eks_tagging()
    secondary_target_group_tagging()
    secondary_launch_template_tagging()

