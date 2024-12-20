from hera.workflows import Container, models, Parameter, Resource


def define_http_serve_resulting_data_container(environment):
    # FIXME: following keeps on running
    # kubectl run nginx-pod --image=harbor.pagoda.os.univ-lyon1.fr/vcity/grim/nginx:1.27 --restart=Never --port=80 -n argo-dev
    return Container(
        name="nginx-server-container",
        inputs=[
            Parameter(name="exposed_dir_subpath"),
        ],
        daemon=True,
        labels={"app": "nginx-server-container"},
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


def define_http_serve_resulting_data_create_service_resource():
    """Returns the Resource that creates the (k8s) Service exposing the pod
    port to the clusterIP (network of nodes)
    """
    manifest = """apiVersion: v1
kind: Service
metadata:
    name: demogrim-resulting-data-http-service
    labels:
        cleanup: "true"
spec:
    type: ClusterIP
    selector:
        app: nginx-server-container
    ports:
    - protocol:   TCP
      port:       80
      targetPort: 80
"""

    return Resource(
        name="create-resulting-data-http-service", action="apply", manifest=manifest
    )


def define_http_serve_resulting_data_create_ingress_resource():
    """
    Returns the Resource that creates the (k8s) Ingress exposing the
    Service to the cluster extranet
    """
    manifest = """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: demogrim-resulting-data-http-ingress
  labels:
    cleanup: "true"
  annotations:
    # automatically creates the tls certificate
    cert-manager.io/cluster-issuer: letsencrypt-pagoda3-prod
spec:
  ingressClassName: traefik
  tls:
  - hosts:
    - data-http.demogrim.pagoda.liris.cnrs.fr
    secretName: demogrim-3dtiles-server-tls-secret
  rules:
  - host: data-http.demogrim.pagoda.liris.cnrs.fr
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: demogrim-resulting-data-http-service
            port:
              number: 80
"""
    return Resource(
        name="create-resulting-data-http-ingress", action="apply", manifest=manifest
    )


def define_http_serve_resulting_data_delete_resources():
    """
    Delete the (k8s) Resources exposing the pod to the cluster extranet
    (that is the Resources with a "cleanup=true" label)
    """
    return Resource(
        name="delete-resulting-data-http-service",
        action="delete",
        flags=["service", "--selector", "cleanup=true"],
    )


### References
# https://kubernetes.io/docs/tutorials/services/connect-applications-service/
# https://kubernetes.io/docs/concepts/services-networking/ingress/
# https://github.com/argoproj-labs/hera/blob/main/docs/examples/workflows/upstream/resource_delete_with_flags.md

############################################################################
# Debugging notes
#
##### Assert directly (as opposed to through the readiness_probe) that the
# container is indeed listening on 80:
# CONTAINER_NAME=`kubectl get pods -l app=nginx-server-container --field-selector=status.phase==Running --output=jsonpath={.items..metadata.name}`
# kubectl get pod ${CONTAINER_NAME}
# kubectl exec --stdin --tty ${CONTAINER_NAME} -- apt update
# kubectl exec --stdin --tty  ${CONTAINER_NAME} -- apt install net-tools
# kubectl exec --stdin --tty  ${CONTAINER_NAME} -- netstat -pln
#   \-----> should return a LISTEN on 80
#
##### Get the container IP
# kubectl get pod ${CONTAINER_NAME} --output=jsonpath={.status.podIPs}
#
##### Check the service is running
# kubectl apply -f resulting_data_http_service.yml
# kubectl get service demogrim-resulting-data-http-service
#    If you try to open the podIP on port 80 then nothing is displayed
#
