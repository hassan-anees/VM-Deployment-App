#!/bin/bash
OLDIFS=$IFS
IFS=","

#debian
debian="Debian:debian-10-daily:10-gen2:0.20200222.178"

#redhat
redhat="RHEL"

#ubuntu
ubuntu="cognosys:ubuntu-1604-lts:ubuntu-16-04-lts:1.2019.0711"

create_vm() {

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
    PUBIP=$(az vm show -d -g myResourceGroup2 -n $1 --query publicIps -o tsv)
    echo "$PUBIP is the ip"

    #reading the docker
    while read name dockerImg registry background
        do
            if [ "$2" == "$redhat" ]; then
                ssh -o "StrictHostKeyChecking no" -n $PUBIP sudo yum install -y docker device-mapper-libs device-mapper-event-libs
                ssh -o "StrictHostKeyChecking no" -n $PUBIP sudo systemctl enable --now docker.service
            else 
                if [ "$2" == "$ubuntu" ]; then
                    sleep 600
                fi
                ssh -o "StrictHostKeyChecking no" -n $PUBIP sudo apt -y install docker.io
                ssh -o "StrictHostKeyChecking no" -n $PUBIP sudo systemctl start docker     
            fi
            ssh -o "StrictHostKeyChecking no" -n $PUBIP sudo docker pull "$dockerImg"
            ssh -o "StrictHostKeyChecking no" -n $PUBIP sudo docker run --rm "$dockerImg"

            echo "$1 $2 $3 $4"
        done < $"dockerFileAzure.csv"

}

# ssh_connection(){

# }

#CHANGE THING LATER
while read platform name os size key
    do
        if [ "$platform" == "Azure" ]; then
            create_vm "$name" "$os" "$size" "$key"
        fi
    done < $"vmConfigAzure.csv"

IFS=$OLDIFS