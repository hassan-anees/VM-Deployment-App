#!/bin/bash
OLDIFS=$IFS
IFS=","

debian="Debian:debian-10-daily:10-gen2:0.20200222.178"
redhat="RHEL"
#ubuntu="cognosys:ubuntu-1604-lts:ubuntu-16-04-lts:1.2019.0711"
ubuntu="Canonical:UbuntuServer:16.04-LTS:latest"

docker1(){
    echo "$1 is the ip"
    ssh -o "StrictHostKeyChecking no" -n $1 sudo apt-get update
    ssh -o "StrictHostKeyChecking no" -n $1 sudo apt -y install docker.io
    ssh -o "StrictHostKeyChecking no" -n $1 sudo systemctl start docker
    ssh -o "StrictHostKeyChecking no" -n $1 sudo docker run --rm $2
}

docker0(){

    ssh -o "StrictHostKeyChecking no" -n $1 sudo yum install -y docker device-mapper-libs device-mapper-event-libs
    ssh -o "StrictHostKeyChecking no" -n $1 sudo systemctl enable --now docker.service
    ssh -o "StrictHostKeyChecking no" -n $1 sudo docker run --rm $2
}

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
    
    echo "name($1) imageId($2) size($3) key($4) "
    #reading the docker
    while read name dockerImg registry background
        do
            # echo "name($name) dockImg($dockerImg) regis($registry) bac($background) "
            if [ "$2" == "$redhat" ]; then
                if [ "$1" == "$name" ]; then
                    echo "FOUND SAME REDHAT"
                    echo "$name $dockerImg $registry $background"
                    docker0 "$IPADDR" "$dockerImg"
                fi
            else 
                if [ "$2" == "$ubuntu" ] || [ "$2" == "$debian" ]; then
                    sleep 1
                    if [ "$1" == "$name" ]; then
                        echo "FOUND FROM DOCKER"
                        echo "$name $dockerImg $registry $background"
                        docker1 "$IPADDR" "$dockerImg"
                    fi     
                fi
            fi
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