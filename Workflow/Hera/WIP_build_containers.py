import os
import sys
import re
import yaml
from docker_helper import DockerHelperBuild

if __name__ == "__main__":

    print("CAVEAT EMPTOR: work in progress...")

    docker_compose_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", ".."
    )
    docker_compose_file = open(os.path.join(docker_compose_dir, "docker-compose.yml"))
    print("Collecting images to build from docker-compose file", docker_compose_file)

    containers_to_build = list()
    docker_compose = yaml.safe_load(docker_compose_file)
    services = docker_compose["services"]
    for service, value in services.items():
        if "profiles" in value.keys():
            print("Dropping build of profiled service", service)
            continue
        if not "build" in value.keys():
            print("Dropping build of service ", service, "with no build section.")
            continue
        build = value["build"]
        if not "image" in value.keys():
            print("Dropping build of service ", service, "with no image section.")
            continue
        image = value["image"]

        if not "context" in build.keys():
            print(
                "Dropping build of service ", service, "with no build/context section."
            )
            continue
        context = build["context"]
        context_dir = os.path.normpath(os.path.join(docker_compose_dir, context))

        if "dockerfile" in build.keys():
            dockerfile = build["dockerfile"]
        else:
            # Implicit dockerfile entry is ... dockerfile
            dockerfile = "dockerfile"

        # For context held within local directories, assert the dockerfile file
        # existence:
        if not re.search("https://", context) and not re.search("http://", context):
            if not os.path.isfile(os.path.join(context_dir, dockerfile)):
                print("No such dockerfile:", dockerfile, "for service", service)
                print("Exiting.")
                sys.exit(1)
        containers_to_build.append((image, context_dir))

    print(containers_to_build)
    for image, context_dir in containers_to_build:
        print("Trying to building image", image, "out of docker context", context_dir)
        building = DockerHelperBuild("bozo", "4.2")
        building.build(context_dir)
