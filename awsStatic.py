from __future__ import print_function
import boto3
import csv
import botocore
import paramiko

ec2 = boto3.resource('ec2', 'us-east-1')
ec2_client = boto3.client('ec2', 'us-east-1')

vmList = []
vmObjectList = []
dockerObjectList = []
dockerRowList = []

# ###########################################
#this is the security group id
groupId = 'sg-030bd326ed117a5b8'

########################################

class VirtualMachine:
    def __init__(self, platform, instanceName, vmName, vmSize, sshkey, storageSpace):
        self.platform = platform
        self.instanceName = instanceName
        self.vmName = vmName
        self.vmSize = vmSize
        self.sshkey = sshkey
        self.storageSpace = storageSpace

class Docker:
    def __init__(self, instanceName, imageName, registry, background):
        self.instanceName = instanceName
        self.imageName = imageName
        self.registry = registry
        self.background = background
 

def fileReader(filename):

    with open(filename, 'r') as file:
        next(file)
        reader = csv.reader(file)
        for row in reader:
            ####NEED TO TAKE IN STORAGE STILL
            vmObj = VirtualMachine(row[0], row[1], row[2], row[3], row[4], row[5])
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
    print('stroage ({})'.format(vmObj.storageSpace))

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


################

def run_command(command, ssh_client):
    #print('run command')
    stdin, stdout, stderr = ssh_client.exec_command(command)
    stdin.flush()
    data = stdout.read().splitlines()
    #print('run command')
    for line in data:
        #print('run command')
        x = line.decode()
        #print(line.decode())
        #print('\n\ntest')
        print(x, line)


# def sshConnection():
#     for instance in ec2.instances.all():
#         print(instance.id, instance.instance_type, instance.state)
#         for instance in ec2.instances.all():
#             print(instance.id, instance.instance_type, instance.state)
    
#             try:
#                 key = paramiko.RSAKey.from_private_key_file("key1.pem")
#                 client = paramiko.SSHClient()
#                 client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#                 client.connect(instance.public_dns_name,username='ec2-user',pkey=key)
        
#                 run_command('sudo yum install -y docker', client)
#                 run_command('sudo service docker start', client)
#                 run_command('sudo usermod -a -G docker ec2-user', client)
#                 run_command('sudo docker run hello-world', client)
#                 client.close()
#             except Exception as e:
#                 print(e)
#                 client.close()

###

#####

def sshConnection():
    instances = ec2.instances.filter(
        Filters=[{'Name':'instance-state-name','Values':['running']}]
        )
    print(instances)
    for instance in instances:
        print(instance.id, instance.instance_type, instance.image_id, instance.public_ip_address, instance.vpc_id)
        print('hello')

    

    try:
        print('testing')
        key = paramiko.RSAKey.from_private_key_file("key1.pem")
        #print('testing2, got key')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect('ec2-3-86-211-135.compute-1.amazonaws.com',username='ec2-user',pkey=key)
        #print('testing3, got key')

        # run_command('sudo yum install -y docker', client)
        # run_command('sudo service docker start', client)
        # run_command('sudo usermod -a -G docker ec2-user', client)
        # run_command('sudo docker run hello-world', client)
        run_command('ls -a', client)
        #run_command('docker pull dastacey/hellocloud', client)
        #run_command('sudo docker run dastacey/hellocloud', client)


        #print('testing4, got key')
        client.close()
    except Exception as e:
        print(e)
        client.close()

def fileReaderDocker(filename):

    with open(filename, 'r') as file:
        next(file)
        reader = csv.reader(file)
        for row in reader:
            ####NEED TO TAKE IN STORAGE STILL
            dockerObj = Docker(row[0], row[1], row[2], row[3])
            print(row)
            dockerRowList.append(row)
            print(dockerRowList)
            dockerObjectList.append(dockerObj)
            #here do a ssh connection 



###########

def main():
    #fileReader('test_deploy_info.csv')
    #listVM()
    sshConnection()
    fileReaderDocker('dockerFile.csv')
    print('\n')
    #print(ec2.instances.all())
    

if __name__ == "__main__":
    main()