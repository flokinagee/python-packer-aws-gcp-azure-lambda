# Abstract class to handle cloud specifics (AWS Lambda, GCP Cloud Function ... etc)
# This cloud specific for AWS #
import sys,os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
import boto3
from botocore.exceptions import ClientError
from packer import Packer

class AbstractPacker(Packer):
    def __init__(self, event, packer_template_file=None, exc=None, only=None, vars=None,
                 var_file=None, exec_path=None, package=None):
        super().__init__(packer_template_file=packer_template_file, exc=exc, only=only, vars=vars,
                 var_file=var_file, exec_path=exec_path, package=package)
        self.event = self._validate_argtype(event or {}, dict)
    
    def share_ami(self,ami_id, accounts):
        client = boto3.client('ec2', region_name='ap-southeast-1')
        self.log("inside sharing")
        try:
            response = client.modify_image_attribute(Attribute='launchPermission',ImageId=ami_id, UserIds=accounts,OperationType='add')
            self.log("shaing success")
        except ClientError as e:
            self.log(e.response['Error'])
            return False
        return response

