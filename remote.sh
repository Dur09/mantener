#!/bin/bash

USERNAME=username
PASSWORDS="pass"
HOSTS="vsui1.som1.marchex.com"
SCRIPT="sudo systemctl restart adtrack-http.service"
for HOSTNAME in ${HOSTS} ; do
    echo "${HOSTS}"
    sshpass -p ${PASSWORDS} ssh -o StrictHostKeyChecking=no -l ${USERNAME} ${HOSTNAME} "${SCRIPT}"
done
