from asyncio.constants import SENDFILE_FALLBACK_READBUFFER_SIZE
import sys
import os
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../"))
import unittest
from unittest import mock
from main import lambda_handler
from botocore.exceptions import ClientError


class BuildTest(unittest.TestCase):
    event = {
        "packer_template_file" : "templates/packer_template.json",
        "packer_binary": "bin/packer",
        "shared_accounts": [ "12345678923"]
        }

    build_ami_output = "AMIs were created:\\nap-southeast-1: ami-123456789dsfs\\n"

    @mock.patch('packer_abstract.boto3')
    @mock.patch('packer.subprocess')
    def test_success_build(self, mock_subproc_popen, mock_boto3):
        proc = mock.Mock()
        mock_subproc_popen.Popen.return_value = proc
        proc.stdout.read.side_effect = [ "Output validation message", self.build_ami_output ]
        proc.stderr.read.side_effect = [ "Error message", "Error build message" ]
        proc.returncode = 0
        mock_boto3.client().modify_image_attribute.return_value = True
        lambda_handler(self.event, context=None)

    @mock.patch('packer_abstract.boto3')
    @mock.patch('packer.subprocess')
    def test_fail_validation(self, mock_subproc_popen, mock_boto3):
        proc = mock.Mock()
        mock_subproc_popen.Popen.return_value = proc
        proc.stdout.read.side_effect = [ "Output validation stage message", self.build_ami_output ]
        proc.stderr.read.side_effect = [ "Error message", "Error build message" ]
        proc.returncode = 1
        mock_boto3.client().modify_image_attribute.return_value = True
        lambda_handler(self.event, context=None)

    @mock.patch('packer_abstract.boto3')
    @mock.patch('packer.subprocess')
    def test_fail_build(self, mock_subproc_popen, mock_boto3):
        proc = mock.Mock()
        type(proc).returncode = mock.PropertyMock(side_effect=[0, 1, 1, 1])
        mock_subproc_popen.Popen.return_value = proc
        proc.stdout.read.side_effect = [ "Output validation stage message",  "AMI Creation Failed" ]
        proc.stderr.read.side_effect = [ "Error message", "Error build message" ]
        mock_boto3.client().modify_image_attribute.return_value = True
        lambda_handler(self.event, context=None)



    @mock.patch('packer_abstract.boto3')
    @mock.patch('packer.subprocess')
    def test_share_ami_access_denied(self, mock_subproc_popen, mock_boto3):
        proc = mock.Mock()
        mock_subproc_popen.Popen.return_value = proc
        proc.stdout.read.side_effect = [ "Output validation stage message", self.build_ami_output ]
        proc.stderr.read.side_effect = [ "Error message", "Error build message" ]
        proc.returncode = 0
        mock_boto3.client().modify_image_attribute.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'access-denied'}}, 'operation')
        lambda_handler(self.event, context=None)



if __name__ == '__main__':
     unittest.main(verbosity=2)
