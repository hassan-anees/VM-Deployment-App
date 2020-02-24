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
 
################

def vmBashCommand(command, ssh_client):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    stdin.flush()
    data = stdout.read().splitlines()
    for line in data:
        string = line.decode()
        print(string)


def get_instance_name(instance):
    for el in instance.tags:
        #turns this into a json format string
        jsonObj = json.dumps(el)
        obj = json.loads(jsonObj)
        return obj['Value']
        

def sshConnection():
    itr = 0

    instances = ec2.instances.filter(
        Filters=[{'Name':'instance-state-name','Values':['pending']}]
        )
  #  print(instances)
    for instance in instances:
        #print(instance.id, instance.instance_type, instance.image_id, instance.public_ip_address, instance.vpc_id, instance.key_name, instance.tags)
        instance.wait_until_running()
        #name = get_instance_name(instance)
        #print(name) 
        
                #print(instance.tags['Name'])
    instances = ec2.instances.filter(
        Filters=[{'Name':'instance-state-name','Values':['running']}]
        )
    #going through every instance running on the cloud
    for instance in instances:
        itr = 0
        #print('ok')
        #another loop going through the dockerObj list 
        print('--------------------------------------------------')
        print('DOCKER at IP ({})'.format(instance.public_ip_address))
        print('--------------------------------------------------')        
        #print(instance.id, instance.instance_type, instance.image_id, instance.public_ip_address, instance.vpc_id, instance.key_name, instance.tags)

        for dockerObj in dockerObjectList:
            itr = itr + 1
            #print('ok')
            #print('i is({})'.format(i))
            #print('name ({})'.format(dockerObj.instanceName))
            # print('imagename ({})'.format(dockerObj.dockerImageName))
            # print('registry ({})'.format(dockerObj.registry))
            # print('background is ({})'.format(dockerObj.background))
            # print('\n')

            instName = get_instance_name(instance)

            if instName == dockerObj.instanceName:
                #print('found match!')
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
                    client = paramiko.SSHClient()
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


                    if instance.image_id == 'ami-07ebfd5b3428b6f4d':
                        user = 'ubuntu'
                    else:
                        user = 'ec2-user'

                    #make sure to also do a if else to check if a image_id is ubuntu. If it is then change ubuntu.
                    client.connect(instance.public_ip_address, username=user,pkey=key)
                    #print('made connection')
                    ##linux 2 and linux ami
                    if instance.image_id == 'ami-0a887e401f7654935' or instance.image == 'ami-0a887e401f7654935':
                        vmBashCommand('sudo usermod -a -G docker ec2-user', client)
                        #vmBashCommand(pullString, client)
                        if dockerObj.background == 'N':
                            vmBashCommand('---------------------------------------------', client)
                            vmBashCommand('echo RUNNING {}'.format(docImage), client)
                            vmBashCommand(runString, client)
                            vmBashCommand('---------------------------------------------', client)

                    #red hat stuff
                    if instance.image_id == 'ami-0c322300a1dd5dc79':
                        vmBashCommand('sudo systemctl start docker', client)
                        vmBashCommand('echo RUNNING {} image'.format(docImage), client)
                        vmBashCommand('sudo systemctl enable docker', client)

                        #vmBashCommand(pullString, client)
                        if dockerObj.background == 'N':
                            vmBashCommand('---------------------------------------------', client)
                            vmBashCommand('echo RUNNING {} image'.format(docImage), client)
                            vmBashCommand(runString, client)
                            vmBashCommand('---------------------------------------------', client)        

                    #SUSE linux
                    if instance.image_id == 'ami-0df6cfabfbe4385b7':
                        vmBashCommand('sudo service docker start', client)
                        vmBashCommand('sudo usermod -a -G docker ec2-user', client)
                        #vmBashCommand(pullString, client)
                        if dockerObj.background == 'N':
                            vmBashCommand('---------------------------------------------', client)
                            vmBashCommand('echo RUNNING {} image'.format(docImage), client)
                            vmBashCommand(runString, client)
                            vmBashCommand('---------------------------------------------', client)
                    #ubuntu
                    if instance.image_id == 'ami-07ebfd5b3428b6f4d' or instance.image_id == 'ami-0400a1104d5b9caa1':
                        vmBashCommand('sudo systemctl start docker', client)
                        #vmBashCommand(pullString, client)
                        if dockerObj.background == 'N':
                            vmBashCommand('---------------------------------------------', client)
                            vmBashCommand('echo RUNNING {} image'.format(docImage), client)
                            vmBashCommand(runString, client)
                            vmBashCommand('---------------------------------------------', client)

                    #print('the length')
                    #print(len(dockerObjectList))
                    # print(itr)
                    # print(len(dockerObjectList))
                    # if itr == len(dockerObjectList) -1 :
                    #     print('IN HEREHEHRHEHRE\n')

                    print('Currently Downloaded (Images)---------------------------------------------')
                    vmBashCommand('sudo docker images', client)
                    print('Currently Running (PS)---------------------------------------------')
                    vmBashCommand('sudo docker ps', client)

                    itr = itr + 1

                    
                    client.close()
                except Exception as e:
                    print(e)
            #itr = itr +1
        print("\n\n")    
            

def fileReaderDocker(filename):

    with open(filename, 'r') as file:
        next(file)
        reader = csv.reader(file)
        for row in reader:
            ####NEED TO TAKE IN STORAGE STILL
            dockerObj = Docker(row[0], row[1], row[2], row[3])
            dockerRowList.append(row)
            dockerObjectList.append(dockerObj)



###########

def main():

    fileReaderDocker('dockerFile.csv')
    sshConnection()
    

if __name__ == "__main__":
    main()