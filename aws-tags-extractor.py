import boto3
import csv
import os

"""
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "tag:GetResources"
            ],
            "Resource": "*"
        },
        {
            "Sid": "ListObjectsInBucket",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::<BUCKET_NAME>"
            ]
        },
        {
            "Sid": "AllObjectActions",
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": [
                "arn:aws:s3:::<BUCKET_NAME>/*"
            ]
        }
    ]
}
"""

output_s3_bucket = "<S3_BUCKET_NAME>"
output_s3_path = "tagged-resources.csv"
output_file_path = "/tmp/tagged-resources.csv"
field_names = ['ResourceArn', 'TagKey', 'TagValue']

def upload_to_s3():
    print("Uploading file {} to s3://{}/{}".format(output_file_path, output_s3_bucket, output_s3_path))
    s3 = boto3.resource('s3')
    s3.Bucket(output_s3_bucket).upload_file(output_file_path, output_s3_path)
    print("Done uploading file {} to s3://{}/{}".format(output_file_path, output_s3_bucket, output_s3_path))

def writeToCsv(writer, tag_list):
    for resource in tag_list:
        if len(resource['Tags']) == 0:
            row = dict(ResourceArn=resource['ResourceARN'], TagKey="", TagValue="")
        else:
            print("Extracting tags for resource: " +resource['ResourceARN'] + "...")            
            for tag in resource['Tags']:
              row = dict(ResourceArn=resource['ResourceARN'], TagKey=tag['Key'], TagValue=tag['Value'])
        writer.writerow(row)

def extract_tags():
    restag = boto3.client('resourcegroupstaggingapi')
    with open(output_file_path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, quoting=csv.QUOTE_ALL,
                                delimiter=',', dialect='excel', fieldnames=field_names)
        writer.writeheader()
        response = restag.get_resources(ResourcesPerPage=50)
        print(response['ResourceTagMappingList'])
        writeToCsv(writer, response['ResourceTagMappingList'])
        while 'PaginationToken' in response and response['PaginationToken']:
            token = response['PaginationToken']
            response = restag.get_resources(
                ResourcesPerPage=50, PaginationToken=token)
            writeToCsv(writer, response['ResourceTagMappingList'])
    print("Gerenated file: {}".format(output_file_path))
    
def lambda_handler(event, context):
    extract_tags()
    upload_to_s3()
