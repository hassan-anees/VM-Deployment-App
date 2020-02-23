from __future__ import print_function
import boto3
import csv
import botocore
import paramiko
import json
import subprocess
import time


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
    def __init__(self, instanceName, dockerImageName, registry, background):
        self.instanceName = instanceName
        self.dockerImageName = dockerImageName
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
        #if its brand new we want to do this to have access to vm
        bashCommand = 'chmod 400 {}.pem'.format(vmObj.sshkey)
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()



    instances = ec2.create_instances(
        BlockDeviceMappings=[{"DeviceName": "/dev/xvda","Ebs" : { "VolumeSize" : int(vmObj.storageSpace) }}],
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


#ena stuff. remove later
# #####
# for instance in instances:
#     print(instance.id, instance.instance_type, instance.state)
#     for instance in instances:
#         print(instance.id, instance.instance_type, instance.state)

#         try:
#             key = paramiko.RSAKey.from_private_key_file("./ena-keyPair.cer")
#             client = paramiko.SSHClient()
#             client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#             client.connect(instance.public_dns_name,username='ec2-user',pkey=key)
    
#             run_command('sudo yum install -y docker', client)
#             run_command('sudo service docker start', client)
#             run_command('sudo usermod -a -G docker ec2-user', client)
#             run_command('sudo docker run hello-world', client)
    
#     client.close()

##


def get_instance_name(instance):
    for el in instance.tags:
        #turns this into a json format string
        jsonObj = json.dumps(el)
        #print(jsonObj)
        #turns to json object
        obj = json.loads(jsonObj)
        return obj['Value']
        

def sshConnection():
    instances = ec2.instances.filter(
        Filters=[{'Name':'instance-state-name','Values':['pending']}]
        )
    print(instances)
    for instance in instances:
        print(instance.id, instance.instance_type, instance.image_id, instance.public_ip_address, instance.vpc_id, instance.key_name, instance.tags)
        print('waiting until its ready')
        instance.wait_until_running()
        #name = get_instance_name(instance)
        #print(name) 

    #######################################
    #REMOVE THIS FOR DEBUGGING, ONLY NEED THIS WHEN YOU initialize vm
    #######################################
    time.sleep(15.0)

                #print(instance.tags['Name'])
    instances = ec2.instances.filter(
        Filters=[{'Name':'instance-state-name','Values':['running']}]
        )
    #going through every instance running on the cloud
    for instance in instances:
        #another loop going through the dockerObj list 
        print('docker image running')
        print(instance.id, instance.instance_type, instance.image_id, instance.public_ip_address, instance.vpc_id, instance.key_name, instance.tags)

        for dockerObj in dockerObjectList:

            print('name ({})'.format(dockerObj.instanceName))
            # print('imagename ({})'.format(dockerObj.dockerImageName))
            # print('registry ({})'.format(dockerObj.registry))
            # print('background is ({})'.format(dockerObj.background))
            # print('\n')

            instName = get_instance_name(instance)
            '''
            #once you found a match, you construct the docker command
            #sudo docker run <background or foreground > <registry if not library>/<dockerImageName>
            Once a name has been found we need to first install and set up docker on the vm
            then run the specified images in the vm
            We first need to pull an image
                sudo docker pull <registry>/<dockerImageName>
                sudo docker run <background, --rm or -d>
            '''
   
        

            if instName == dockerObj.instanceName:
                print('found match!')
                background = ""
                docImage = ""
                libFlag = False

                if dockerObj.background == 'N':
                    background = '--rm'
                else:
                    background = '-d'

                if dockerObj.registry == 'library':
                    docImage = dockerObj.dockerImageName
                    libFlag = True
                else:
                    docImage = '{}/{}'.format(dockerObj.registry, dockerObj.dockerImageName)
                #sudo.. blah blah BACKGROUND DOCIMAGE
                pullString = 'sudo docker pull {}'.format(docImage)
                runString = 'sudo docker run {} {}'.format(background, docImage)
                #print(runString)
            
                try:
                    #make this dynamic later. like pull the key that an instance uses through some command
                # i think you do instance.key_name
                    time.sleep(1.2)
                    key = paramiko.RSAKey.from_private_key_file(instance.key_name + '.pem')
                    print('got pem stuff')
                    client = paramiko.SSHClient()
                    print('got client')
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    print('got client host keys')


                    if instance.image_id == 'ami-07ebfd5b3428b6f4d':
                        user = 'ubuntu'
                    else:
                        user = 'ec2-user'

                    #here put the dns, or up of it
                    #make sure to also do a if else to check if a image_id is ubuntu. If it is then change ubuntu.
                    client.connect(instance.public_ip_address, username=user,pkey=key)
                    print('make connection')

                    print('-----------------------')
                    run_command('ls -a', client)
                    print('-----------------------')
                    ##linux 2 and linux ami
                    if instance.image_id == 'ami-0a887e401f7654935' or instance.image == 'ami-0a887e401f7654935':
                        run_command('sudo yum install -y docker', client)
                        run_command('sudo service docker start', client)
                        run_command('sudo usermod -a -G docker ec2-user', client)
                        run_command(pullString, client)
                        run_command(runString, client)

                    #red hat stuff
                    if instance.image_id == 'ami-0c322300a1dd5dc79':
                        run_command('sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo', client)
                        run_command('sudo dnf repolist -v', client)
                        run_command('sudo dnf -y install docker-ce-3:18.09.1-3.el7', client)
                        run_command('sudo dnf -y install https://download.docker.com/linux/centos/7/x86_64/stable/Packages/containerd.io-1.2.6-3.3.el7.x86_64.rpm', client)
                        run_command('sudo systemctl start docker', client)
                        run_command('sudo systemctl enable docker', client)

                        run_command(pullString, client)
                        run_command(runString, client)
                    #SUSE linux
                    if instance.image_id == 'ami-0df6cfabfbe4385b7':
                        run_command('sudo service docker start', client)
                        run_command('sudo usermod -a -G docker ec2-user', client)
                        run_command(pullString, client)
                        run_command(runString, client)
                    #ubuntu
                    if instance.image_id == 'ami-07ebfd5b3428b6f4d':
                        run_command('sudo apt-get update', client)
                        run_command('sudo apt -y install docker.io', client)
                        run_command('sudo systemctl start docker', client)

                        run_command(pullString, client)
                        run_command(runString, client)

                    
                    
            


                    # run_command('sudo yum install -y docker', client)
                    # run_command('sudo service docker start', client)
                    # run_command('sudo usermod -a -G docker {}'.format(user), client)


                    # run_command(pullString, client)
                    # run_command(runString, client)

                    #print('testing4, got key')
                    client.close()
                except Exception as e:
                    print(e)

def fileReaderDocker(filename):

    with open(filename, 'r') as file:
        next(file)
        reader = csv.reader(file)
        for row in reader:
            ####NEED TO TAKE IN STORAGE STILL
            dockerObj = Docker(row[0], row[1], row[2], row[3])
            #print(row)
            dockerRowList.append(row)
            #print(dockerRowList)
            dockerObjectList.append(dockerObj)
            #here do a ssh connection 



###########

def main():
    fileReader('deploy_info.csv')
    #listVM()
    fileReaderDocker('dockerFile.csv')
    sshConnection()
    print('\n')
    #print(ec2.instances.all())
    

if __name__ == "__main__":
    main()