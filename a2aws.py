from __future__ import print_function
import boto3
import csv

ec2 = boto3.resource('ec2', 'us-east-1')
ec2_client = boto3.client('ec2', 'us-east-1')

vmList = []
vmObjectList = []

# ###########################################
#this is the security group id
groupId = 'sg-030bd326ed117a5b8'

########################################

class VirtualMachine:
    def __init__(self, platform, instanceName, vmName, vmSize, sshkey):
        self.platform = platform
        self.instanceName = instanceName
        self.vmName = vmName
        self.vmSize = vmSize
        self.sshkey = sshkey


def fileReader(filename):

    with open(filename, 'r') as file:
        next(file)
        reader = csv.reader(file)
        for row in reader:
            ####NEED TO TAKE IN STORAGE STILL
            vmObj = VirtualMachine(row[0], row[1], row[2], row[3], row[4])
            # print(row)
            createVM(vmObj)
            vmList.append(row)
            vmObjectList.append(vmObj)


'''
got instanceName, vmName, vmSize, 
missing how to set storage size
'''
def create_ssh(sshkey):
   
    try:
        # create a file to store the key locally
        outfile = open(sshkey+".pem",'w')
        # call the boto ec2 function to create a key pair
        key_pair = ec2.create_key_pair(KeyName=sshkey)
        # capture the key and store it in a file
        KeyPairOut = str(key_pair.key_material)
        print(KeyPairOut)
        outfile.write(KeyPairOut)
    except Exception as e:
        print('Key already exists')


def createVM(vmObj):
    print('\n')
    print('platform ({})'.format(vmObj.platform))
    print('instance name ({})'.format(vmObj.instanceName))
    print('VmName ({})'.format(vmObj.vmName))
    print('sizeofVM ({})'.format(vmObj.vmSize))
    print('key ({})'.format(vmObj.sshkey))
    ####NEED TO SAY print for storage

    if vmObj.sshkey == '':
        print('not found, creating')
        vmObj.sshkey = 'MyKeyPair'
    else:
        create_ssh(vmObj.sshkey)



    instances = ec2.create_instances(
        BlockDeviceMappings=[{"DeviceName": "/dev/xvda","Ebs" : { "VolumeSize" : 10 }}],
        ImageId = vmObj.vmName, #VM NAME
        MinCount=1,
        MaxCount=1,
        InstanceType= vmObj.vmSize, #this is VM SIZE
        KeyName= vmObj.sshkey, #/Users/hassananees/.ssh/MyKeyPair.pem
        SecurityGroupIds=[groupId,], 
        TagSpecifications=[ #INSTANCE NAME
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name', #this sets the name of the VM
                    'Value': vmObj.instanceName # this is what the name will be
                },
            ]
        },
        ],
    )

    print('created')


def listVM():
    for instance in ec2.instances.all():
        print(
            "Id: {0}\nPlatform: {1}\nType: {2}\nPublic IPv4: {3}\nAMI: {4}\nState: {5}\n".format(
            instance.id, instance.platform, instance.instance_type, instance.public_ip_address, instance.image.id, instance.state
            )
        )



def main():
    print('\n')
    fileReader('aws_deploy_info.csv')
    #listVM()
    print('\n')
    print(ec2.instances.all())


    

if __name__ == "__main__":
    main()