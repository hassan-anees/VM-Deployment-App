from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import DiskCreateOption



#################below is the  azure stuff
#######################


def createVm():
    VM_PARAMETERS={
            'location': 'LOCATION', #This is the location based '
            'os_profile': {
                'computer_name': 'VM_NAME',
                'admin_username': 'USERNAME',
                'admin_password': 'PASSWORD'
            },
            'hardware_profile': {
                'vm_size': 'Standard_DS1_v2' # this is where you select the size of the VM 'Size'
            },
            'storage_profile': {
                'image_reference': {
                    'publisher': 'Canonical', 
                    'offer': 'UbuntuServer',
                    'sku': '16.04.0-LTS',
                    'version': 'latest'
                },
            },
            'network_profile': {
                'network_interfaces': [{
                    'id': 'NIC_ID',
                }]
            },
        }

    compute_client.virtual_machines.create_or_update(
        'RESOURCE_GROUP_NAME', 'VM_NAME', VM_PARAMETERS)


def main():
    print('\n')
    createVm()
    listVM()

    print(ec2.instances.all())


    

if __name__ == "__main__":
    main()