#!/bin/bash
OLDIFS=$IFS
IFS=","

machines=$(az vm list --query "[].osProfile.computerName" -o tsv)

for machine in $machines; do
    options=$(az vm show -d -g myResourceGroup2 -n $machine --query "[name, powerState, publicIps, storageProfile.imageReference.offer, location]" -o tsv)
    IFS=$'\n' arr=( $options )
   
    IFS=","

    #reading the docker
    while read name dockerImg registry background
        do
          # echo "($arr)"
          # echo "$name"
          # echo "${arr[0]}"
          if [ "${arr[0]}" == "$name" ]; then
            echo "The IP is ${arr[2]}"
            echo "Docker Current downloaded images"
            ssh -o "StrictHostKeyChecking no" -n ${arr[2]} sudo docker images
            echo "Docker Running images"
            ssh -o "StrictHostKeyChecking no" -n ${arr[2]} sudo docker ps
          fi
        done < $"dockerFileAzure.csv"


  
done

IFS=$OLDIFS
