import os, uuid
import json
import string
import csv



vmList = []
vmObjectList = []

class VirtualMachine:
    def __init__(self, platform, instanceName, vmName, vmSize, sshkey):
        self.instanceName = instanceName
        self.vmName = vmName
        self.vmSize = vmSize
        self.storageSize = storageSize
        self.sshkey = sshkey


def fileReader(filename):

    with open(filename, 'r') as file:
        next(file)
        reader = csv.reader(file)
        for row in reader:
            vm1 = VirtualMachine(row[0], row[1], row[2], row[3], row[4])
            print(row)
            vmList.append(row)
            vmObjectList.append(vm1)





def main():
    # print('readinf csv\n')
    fileReader('deploy_info.csv') 
    # print(vmList)


    # vm1 = AwsVm()
    # vm1.instanceName = 'virtual1'
    # vm1.storageSize = 9
    # vm1.vmName = 'ami-123'
    # vm1.vmSize = 't2.micro'

    # vm1.introduce()


    # print(vmList)  

if __name__ == "__main__":
    main()


