from hera.workflows import Container, Label, models, Parameter


def define_http_serve_resulting_data_container(environment):
    # FIXME: following keeps on running
    # kubectl run nginx-pod --image=harbor.pagoda.os.univ-lyon1.fr/vcity/grim/nginx:1.27 --restart=Never --port=80 -n argo-dev
    return Container(
        name="nginx-server-container",
        inputs=[
            Parameter(name="exposed_dir_subpath"),
        ],
        daemon=True,
        labels=Label(key="app", value="nginx-server-container"),
        image=environment.cluster.docker_registry
        + "/"
        + environment.cluster.docker_organisation
        + "/"
        + "nginx:1.27",
        readiness_probe=models.Probe(
            http_get=models.HTTPGetAction(
                path="/",
                port=80,
            ),
            initial_delay_seconds=2,
            timeout_seconds=1,
        ),
        # The nginx container default configuration file state that the
        # the default exposed directory is as be seen with
        # docker pull nginx
        # docker run -it nginx /bin/bash
        #    root@xyz grep include /etc/nginx/nginx.conf | grep conf
        #              \---> include /etc/nginx/conf.d/*.conf;
        #  and
        #    root@xyz grep root /etc/nginx/conf.d/default.conf
        #              \---> root   /usr/share/nginx/html;
        # Hence the mount_path value for the volume
        volume_mounts=[
            models.VolumeMount(
                name="dummy",
                mount_path="/usr/share/nginx/html",
                sub_path="{{inputs.parameters.exposed_dir_subpath}}",
            )
        ],
    )
