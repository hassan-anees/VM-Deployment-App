from __future__ import print_function
import boto3

ec2 = boto3.resource('ec2', 'us-east-1')


def create_ssh(sshkey):
    # create a file to store the key locally
    outfile = open(sshkey + ".pem",'w')
    # call the boto ec2 function to create a key pair
    try:
        key_pair = ec2.create_key_pair(KeyName=sshkey)
        # capture the key and store it in a file
        KeyPairOut = str(key_pair.key_material)
        print(KeyPairOut)
        outfile.write(KeyPairOut)
    except Exception as e:
        print('Already exists')

key = 'ec2key'
create_ssh(key)

instances = ec2.create_instances(
     ImageId='ami-0e2ff28bfb72a4e45',
     MinCount=1,
     MaxCount=1,
     InstanceType='t2.micro',
     KeyName=key,
    TagSpecifications=[ #INSTANCE NAME
    {
        'ResourceType': 'instance',
        'Tags': [
            {
                'Key': 'Name', #this sets the name of the VM
                'Value': 'vm1'# this is what the name will be
            },
        ]
    },
    ],
 )

for instance in ec2.instances.all():
    print("Id: {0}\nPlatform: {1}\nType: {2}\nPublic IPv4: {3}\nAMI: {4}\nState: {5}\n".format(instance.id, instance.platform, instance.instance_type, instance.public_ip_address, instance.image.id, instance.state))

