#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License").
#    You may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


from typing import Any,  Dict,  Optional

import os,yaml, sys
from aws_codeseeder import _bundle

import subprocess
from aws_codeseeder import LOGGER
from aws_codeseeder.services import codebuild



def run(
    local_deploy_path:str,
    bundle_zip: str,
    buildspec: Dict[str, Any],
    env_vars: Dict[str, str]
    
) -> Optional[codebuild.BuildInfo]:

    current_path = local_deploy_path
    
    #write the buildspec to file
    def write_it(filename, content):
        with open(filename, "w") as buildspec:
            buildspec.write(yaml.dump(content, indent=4))
    write_it(os.path.join(current_path, "buildspec.yaml"),buildspec)

    # Write the environment variables to the file
    env_vars_path = os.path.join(current_path, 'diw.env')   
    with open(env_vars_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f'{key}={value}\n')
            
    ## Extract the zip to the local root so it is mounted by the container
    _bundle.extract_zip(bundle_zip, current_path)


    # docker_command = f"""docker run -it -v /var/run/docker.sock:/var/run/docker.sock \
    # -e "IMAGE_NAME=public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:4.0" \
    # -e "ARTIFACTS={current_path}/artifacts" \
    # -e "SOURCE={current_path}/" \
    # -e "BUILDSPEC={current_path}/buildspec.yaml" \
    # -v "{current_path}/:/LocalBuild/envFile/" \
    # -e "ENV_VAR_FILE=diw.env" \
    # -e "AWS_CONFIGURATION=/home/dgraeber/.aws" \
    # -e "AWS_EC2_METADATA_DISABLED=true" \
    # -e "MOUNT_SOURCE_DIRECTORY=TRUE" \
    # -e "INITIATOR=dgraeber" \
    # public.ecr.aws/codebuild/local-builds:latest"""
    
    #print(docker_command)

    docker_command = [
        "docker","run","-it",
            "-v","/var/run/docker.sock:/var/run/docker.sock",
            "-e", "IMAGE_NAME=public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:4.0",
            "-e", f"ARTIFACTS={current_path}/artifacts" ,
            "-e", f"SOURCE={current_path}/" ,
            "-e", f"BUILDSPEC={current_path}/buildspec.yaml" ,
            "-v", f"{current_path}/:/LocalBuild/envFile/" ,
            "-e", "ENV_VAR_FILE=diw.env" ,
            "-e", "AWS_CONFIGURATION=/home/dgraeber/.aws" ,
            "-e", "AWS_EC2_METADATA_DISABLED=true" ,
            "-e", "MOUNT_SOURCE_DIRECTORY=TRUE" ,
            "-e", "INITIATOR=dgraeber" ,
            "public.ecr.aws/codebuild/local-builds:latest"]


    print(" ".join(docker_command))

    try:
        subprocess.run(docker_command, check=True)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
   

    return None
