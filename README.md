packer to run in lambda in multicloud (AWS GCP Azure) to automate AMI Creation for Immutable deloyment
=============


Python3 Interface for cloudagnostic build [packer.io](http://www.packer.io)

## Version
Python Version = 3.x

## HOWTO
1) Clone repo

git clone https://github.com/flokinagee/python-packer-aws-gcp-azure-lambda.git

cd python-packer-aws-gcp-azure-lambda

2) create virtual env

python3 -m venv env

source env/bin/activate

3) install library

pip install -r requirements.txt -t lib/

4) Invoke main_handler for ami creation

python3 main.py

## Methods ###

#Install

Installation will be done during object instantiation if exec_path file is not found. Package binary will be in directory pakages/packer.zip (download - https://www.packer.io/downloads )

build = Packer(exec_path="bin/packer", package="package/packer.zip", packer_template_file="templates/packer_template.json")


#Verions - checking packer version

build.version()

Packer v1.7.10

#Validate - Validate packer template before build ( templates will be in directory tempplates/)

build.validate().output

'The configuration is valid.\n'

#Build -  Build an AMI

build.build().output

'...1645183105,,ui,say,--> amazon-ebs: AMIs were created:\\nap-southeast-1: ami-0c0513e4027c8eeaa\\n"


##### Other method are in progress to such as fix, clean ###
Packer baseclass reference from https://github.com/nir0s/python-packer but converted from sh module to subprocess as sh module tries to open pty for ec2 connection which is restriced in AWS Lambda

Code is in progress for GCP Azure


## Testing

pytest -v

or

python test_packer.py

or

make test

## Contributions..

..are always welcome.
