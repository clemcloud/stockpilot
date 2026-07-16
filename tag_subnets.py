import boto3
ec2 = boto3.client('ec2', region_name='us-east-1')
subnets = ['subnet-01b275e4ec78bc07f', 'subnet-03435b3b6cf3672e8']
ec2.create_tags(Resources=subnets, Tags=[{'Key':'kubernetes.io/role/elb', 'Value':'1'}, {'Key':'kubernetes.io/cluster/stockpilot-cluster', 'Value':'shared'}])
print('Subnets tagged successfully!')
