#!/bin/bash


az vm create \
    --resource-group vms \
    --name cli-1 \
    --image UbuntuLTS \
    --admin-username azureuser \
    --size Basic_A1 \
    --verbose \
    --generate-ssh-keys