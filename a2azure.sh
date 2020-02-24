#!/bin/bash
OLDIFS=$IFS
IFS=","

debian="Debian:debian-10-daily:10-gen2:0.20200222.178"
redhat="RHEL"
ubuntu="cognosys:ubuntu-1604-lts:ubuntu-16-04-lts:1.2019.0711"

createVm() {

    #first need create resource
    az group create --name myResourceGroup2 --location eastus

    az vm create \
    --resource-group myResourceGroup2 \
    --name "$1" \
    --image "$2" \
    --ssh-key-value @./"$4"

    az vm open-port --port 80 --resource-group myResourceGroup2 --name "$1"

    #going to read the docker file. so have a while loop 
    #in that while loop when you read it, create 
    # #here get the ip 
    IPADDR=$(az vm show -d -g myResourceGroup2 -n $1 --query publicIps -o tsv)
    echo "$IPADDR is the ip"

    #reading the docker
    while read name dockerImg registry background
        do
            if [ "$2" == "$redhat" ]; then
                ssh -o "StrictHostKeyChecking no" -n $IPADDR sudo yum install -y docker device-mapper-libs device-mapper-event-libs
                ssh -o "StrictHostKeyChecking no" -n $IPADDR sudo systemctl enable --now docker.service
            else 
                if [ "$2" == "$ubuntu" ]; then
                    sleep 600
                fi
                ssh -o "StrictHostKeyChecking no" -n $IPADDR sudo apt -y install docker.io
                ssh -o "StrictHostKeyChecking no" -n $IPADDR sudo systemctl start docker     
            fi
            ssh -o "StrictHostKeyChecking no" -n $IPADDR sudo docker pull "$dockerImg"
            ssh -o "StrictHostKeyChecking no" -n $IPADDR sudo docker run --rm "$dockerImg"

        done < $"dockerFileAzure.csv"

}

# ssh_connection(){

# }

#CHANGE THING LATER
while read platform name imageId imageSize key
    do
        if [ "$platform" == "Azure" ]; then
            createVm "$name" "$imageId" "$imageSize" "$key"
        fi
    done < $"vmConfigAzure.csv"

IFS=$OLDIFS