from packer_abstract import AbstractPacker as Runner

def lambda_handler(event, context):
    Runner.log(event)
    try:
        template_file = event['packer_template_file']
        packer_bin  = event['packer_binary']
    except KeyError as e:
        raise e

    build = Runner(event, packer_template_file=template_file, exec_path=packer_bin)
    build_response = build.run_build(event)
    build.log(build_response)


event = {
    "packer_template_file" : "templates/packer_template.json",
    "packer_binary": "bin/mac/packer",
    "shared_accounts": [ "885231250983"]

}

if __name__ == "__main__":
    lambda_handler(event, context=None)
