from modulefinder import packagePathMap
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../lib'))
#import jinja2
import subprocess
import json
from io import StringIO
import zipfile


class Packer():
    """A packer client
    """
    def __init__(self, packer_template_file=None, exc=None, only=None, vars=None,
                 var_file=None, exec_path=None, package=None):
        """
        :param string packer_template_file: Path to Packer template file
        :param list exc: List of builders to exclude
        :param list only: List of builders to include
        :param dict vars: key=value pairs of template variables
        :param string var_file: Path to variables file
        :param string exec_path: Path to Packer executable incase to install
        :param string binary: packer binary/executable
        """
        self.packerfile = self._validate_argtype(packer_template_file, str)
        self.var_file = var_file
        if not os.path.isfile(self.packerfile):
            raise OSError('packerfile not found at path: {0}'.format(
                self.packerfile))
        self.exc = self._validate_argtype(exc or [], list)
        self.only = self._validate_argtype(only or [], list)
        self.vars = self._validate_argtype(vars or {}, dict)
        
        self.packer = list()
        self.exec_path = exec_path if os.path.isfile(exec_path) else self._install(exec_path, package)
        self.packer.append(self.exec_path)

    @staticmethod
    def log(message):
        obj = {
            "Message": message
        }
        print(json.dumps(obj, sort_keys=True, default=str))

    def _append_base_arguments(self):
        """Appends base arguments to packer commands.
        -except, -only, -var and -var-file are appeneded to almost
        all subcommands in packer. As such this can be called to add
        these flags to the subcommand.
        """
        if self.exc and self.only:
            raise PackerException('Cannot provide both "except" and "only"')
        elif self.exc:
            self._add_opt('-except={0}'.format(self._join_comma(self.exc)))
        elif self.only:
            self._add_opt('-only={0}'.format(self._join_comma(self.only)))
        for var, value in self.vars.items():
            self._add_opt("-var")
            self._add_opt("{0}={1}".format(var, value))
        if self.var_file:
            self._add_opt('-var-file={0}'.format(self.var_file))


    def _add_opt(self, option):
        if option:
            self.packer_cmd.append(option)

    def _validate_argtype(self, arg, argtype):
        if not isinstance(arg, argtype):
            raise PackerException('{0} argument must be of type {1}'.format(
                arg, argtype))
        return arg

    def build(self, parallel=False, debug=False, force=False,
              machine_readable=True):
        """Executes a `packer build`
        :param bool parallel: Run builders in parallel
        :param bool debug: Run in debug mode
        :param bool force: Force artifact output even if exists
        :param bool machine_readable: Make output machine-readable
        """
        self.packer_cmd = self.packer[:]
        self.packer_cmd.append('build')

        self._add_opt('-parallel=true' if parallel else None)
        self._add_opt('-debug' if debug else None)
        self._add_opt('-force' if force else None)
        self._add_opt('-machine-readable' if machine_readable else None)
        self._append_base_arguments()
        self._add_opt(self.packerfile)
        try:
            response = subprocess.Popen(self.packer_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            response.wait()
        except Exception as e:
            self.log("Calling Subprocess failed : {}" .format(str(e)))
            response = ResponseObject()
            response.stderr = StringIO("subprocess invocation failed")
            response.returncode = 1
            response.stdout = StringIO()
        finally:
            response.output = response.stderr.read()  + response.stdout.read()
        
        return response

    def version(self):
        """Returns Packer's version number (`packer version`)
        As of v0.7.5, the format shows when running `packer version`
        is: Packer vX.Y.Z. This method will only returns the number, without
        the `packer v` prefix so that you don't have to parse the version
        yourself.
        """
        self.packer_cmd = self.packer[:]
        self.packer_cmd.append('version')
        return subprocess.run(self.packer_cmd)

    def validate(self, syntax_only=False):
        """Validates a Packer Template file (`packer validate`)
        If the validation failed, an `sh` exception will be raised.
        :param bool syntax_only: Whether to validate the syntax only
        without validating the configuration itself.
        """
        self.packer_cmd = self.packer[:]
        self.packer_cmd.append('validate')
        self._add_opt('-syntax-only' if syntax_only else None)
        self._append_base_arguments()
        self._add_opt(self.packerfile)

        try:
            response = subprocess.Popen(self.packer_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            response.wait()
        except Exception as e:
            self.log("Calling Subprocess failed : {}" .format(str(e)))
            response = ResponseObject()
            response.stderr = StringIO("subprocess invocation failed")
            response.returncode = 1
            response.stdout = StringIO()
        finally:
            response.output = response.stderr.read()  + response.stdout.read() 
        return response

    def push(self, create=True, token=False):
        self.packer_cmd = self.packer[:]
        self.packer_cmd.append('push')

        self._add_opt('-create=true' if create else None)
        self._add_opt('-tokn={0}'.format(token) if token else None)
        self._add_opt(self.packerfile)

        return subprocess.run(self.packer_cmd())

    def inspect(self, mrf=True):
        """Inspects a Packer Templates file (`packer inspect -machine-readable`)
        To return the output in a readable form, the `-machine-readable` flag
        is appended automatically, afterwhich the output is parsed and returned
        as a dict of the following format:
          "variables": [
            {
              "name": "aws_access_key",
              "value": "{{env `AWS_ACCESS_KEY_ID`}}"
            },
            {
              "name": "aws_secret_key",
              "value": "{{env `AWS_ACCESS_KEY`}}"
            }
          ],
          "provisioners": [
            {
              "type": "shell"
            }
          ],
          "builders": [
            {
              "type": "amazon-ebs",
              "name": "amazon"
            }
          ]
        :param bool mrf: output in machine-readable form.
        """
        self.packer_cmd = self.packer[:]
        self.packer_cmd.append('inspect')

        self._add_opt('-machine-readable' if mrf else None)
        self._add_opt(self.packerfile)
        return subprocess.run(self.packer_cmd())

        # if mrf:
        #     result.parsed_output = self._parse_inspection_output(
        #                                                 result.stdout.decode())
        # else:
        #     result.parsed_output = None
        # return result

    def fix(self, to_file=None):
        """Implements the `packer fix` function
        :param string to_file: File to output fixed template to
        """
        self.packer_cmd = self.packer[:]
        self.packer_cmd.append('fix')

        self._add_opt(self.packerfile)
        return subprocess.run(self.packer_cmd())
        
        # result = self.packer_cmd()
        # if to_file:
        #     with open(to_file, 'w') as f:
        #         f.write(result.stdout.decode())
        # result.fixed = json.loads(result.stdout.decode())
        # return result


    def _join_comma(self, lst):
        """Returns a comma delimited string from a list"""
        return str(','.join(lst))

    def _parse_inspection_output(self, output):
        """Parses the machine-readable output `packer inspect` provides.
        See the inspect method for more info.
        This has been tested vs. Packer v0.7.5
        """
        parts = {'variables': [], 'builders': [], 'provisioners': []}
        for line in output.splitlines():
            line = line.split(',')
            if line[2].startswith('template'):
                del line[0:2]
                component = line[0]
                if component == 'template-variable':
                    variable = {"name": line[1], "value": line[2]}
                    parts['variables'].append(variable)
                elif component == 'template-builder':
                    builder = {"name": line[1], "type": line[2]}
                    parts['builders'].append(builder)
                elif component == 'template-provisioner':
                    provisioner = {"type": line[1]}
                    parts['provisioners'].append(provisioner)
        return parts

    def _install(self, exec_path, packer_binary):
        fpath, fname = os.path.split(exec_path)
        with open(packer_binary, 'rb') as f:
            zip = zipfile.ZipFile(f)
            for path in zip.namelist():
                zip.extract(path, fpath)
        exec_path = os.path.join(fpath, fname)
        if not self._verify_packer_installed(exec_path):
            raise PackerException('packer installation failed. '
                                  'Executable could not be found under: '
                                  '{0}'.format(exec_path))
        else:
            return exec_path

    def _verify_packer_installed(self, packer_path):
        return os.path.isfile(packer_path)


    def run_build(self, event):
        status = { "status" : False, "ami_id" : None, "shared" : None, "comment": None}
        validation_response = self.validate()
        if validation_response.returncode != 0:
            self.log("validation failed {}" .format(validation_response.output))
            status['comment'] = 'Validation failed'
            return status

        self.log("Build is in progress")
        response = self.build()
        if response.output:
            for line in response.output.split("\n"):
                if 'AMIs were created:' in line:
                    ami_id = line.split(' ')[-1].replace('\\n', '')
                """ detailed cloud watch logs"""
                self.log(line)
        if response.returncode == 0:
            self.log("share AMI with {}" .format(event['shared_accounts']))
            if self.share_ami(ami_id, event['shared_accounts']):
                status = { "status" : True, "ami_id" : ami_id, "shared": event['shared_accounts']}
            else:
                status = { "status" : False, "ami_id" : ami_id, "shared": "failed sharing {}" .format(event['shared_accounts'])}
        return status

class PackerException(Exception):
    pass

class ResponseObject():
    pass