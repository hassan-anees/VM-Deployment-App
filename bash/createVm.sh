#!/bin/bash

#first need create resource
# az group create --name myResourceGroup2 --location eastus

# az vm create \
#   --resource-group myResourceGroup2 \
#   --name myVM2 \
#   --image UbuntuLTS \
#   --admin-username azureuser \
#   --generate-ssh-keys

# az vm open-port --port 80 --resource-group myResourceGroup2 --name myVM2

# #here get the ip 
PUBIP=$(az vm show -d -g myResourceGroup2 -n myVM2 --query publicIps -o tsv)
echo "$PUBIP is the ip"
