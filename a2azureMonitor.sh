#!/bin/bash


machines=$(az vm list --query "[].osProfile.computerName" -o tsv)

for machine in $machines; do
    options=$(az vm show -d -g myResourceGroup2 -n $machine --query "[name, powerState, publicIps, storageProfile.imageReference.offer, location]" -o tsv)
    IFS=$'\n' arr=( $options )
    # echo "VM Name = ${arr[0]}"
    # echo "Current Machine State = ${arr[1]}"
    # echo "Public IP Address = ${arr[2]}"
    # echo "OS Name = ${arr[3]}"
    # echo "Region = ${arr[4]}"
    echo ""
    IFS=","

    # while read name dockerImg registry background
    #     do
    #       # echo "($arr)"
    #       # echo "$name"
    #       # echo "${arr[0]}"
          # if [ "${arr[0]}" == "$name" ]; then
    echo "The IP is ${arr[2]}"
    echo "Docker Current downloaded images"
    ssh -o "StrictHostKeyChecking no" -n ${arr[2]} sudo docker images
    echo "Docker Running images"
    ssh -o "StrictHostKeyChecking no" -n ${arr[2]} sudo docker ps
          # fi
        # done < $"dockerFileAzure.csv"

    # ssh -o "StrictHostKeyChecking no" -n ${arr[2]} sudo docker images
    # echo ""
    # ssh -o "StrictHostKeyChecking no" -n ${arr[2]} sudo docker ps

    # sleep 5

  echo ""
  
done

