from pulumi import Config, export, get_project, get_stack, Output, ResourceOptions
from pulumi_gcp.config import project, zone
from pulumi_gcp.container import Cluster, ClusterNodeConfigArgs
from pulumi_kubernetes import Provider
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.core.v1 import ContainerArgs, PodSpecArgs, PodTemplateSpecArgs, Service, ServicePortArgs, ServiceSpecArgs
from pulumi_kubernetes.meta.v1 import LabelSelectorArgs, ObjectMetaArgs
from pulumi_random import RandomPassword


### Definicion de variables ###

config = Config(None)

# node_count es el numero de nodos, por defecto se configura 1
NODE_COUNT = config.get_int('node_count') or 1

# node_machine_type es el size de los nodos usados por gke, por defecto se utiliza un n1-standard-1 

NODE_MACHINE_TYPE = config.get('node_machine_type') or 'n1-standard-1'

# por defecto se utiliza el usuario 'admin'
USERNAME = config.get('username') or 'admin'

# password por default para el usuario admin
PASSWORD = config.get_secret('password') or RandomPassword("password", length=20, special=True).result

# version de nodo master, por defecto se utiliza la version 1.20 
MASTER_VERSION = config.get('master_version') or '1.20'

### Creacion de cluster ###
 
k8s_cluster = Cluster('gke-cluster',
    initial_node_count=NODE_COUNT,
    node_version=MASTER_VERSION,
    min_master_version=MASTER_VERSION,
    node_config=ClusterNodeConfigArgs(
        machine_type=NODE_MACHINE_TYPE,
        oauth_scopes=[
            'https://www.googleapis.com/auth/compute',
            'https://www.googleapis.com/auth/devstorage.read_only',
            'https://www.googleapis.com/auth/logging.write',
            'https://www.googleapis.com/auth/monitoring'
        ],
    ),
)

### Creacion de kubeconfig ###

k8s_info = Output.all(k8s_cluster.name, k8s_cluster.endpoint, k8s_cluster.master_auth)
k8s_config = k8s_info.apply(
    lambda info: """apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: {0}
    server: https://{1}
  name: {2}
contexts:
- context:
    cluster: {2}
    user: {2}
  name: {2}
current-context: {2}
kind: Config
preferences: {{}}
users:
- name: {2}
  user:
    auth-provider:
      config:
        cmd-args: config config-helper --format=json
        cmd-path: gcloud
        expiry-key: '{{.credential.token_expiry}}'
        token-key: '{{.credential.access_token}}'
      name: gcp
""".format(info[2]['cluster_ca_certificate'], info[1], '{0}_{1}_{2}'.format(project, zone, info[0])))

# Definicion de Kubernetes provider 
k8s_provider = Provider('gke_k8s', kubeconfig=k8s_config)

### Despliegue GKE ###

# Create a canary deployment to test that this cluster works.
labels = { 'app': 'api-{0}-{1}'.format(get_project(), get_stack()) }
canary = Deployment('api',
    spec=DeploymentSpecArgs(
        selector=LabelSelectorArgs(match_labels=labels),
        replicas=1,
        template=PodTemplateSpecArgs(
            metadata=ObjectMetaArgs(labels=labels),
            spec=PodSpecArgs(containers=[ContainerArgs(name='api', image='gcr.io/groovy-legacy-312114/api:latest')]),
        ),
    ), opts=ResourceOptions(provider=k8s_provider)
)

ingress = Service('ingress',
    spec=ServiceSpecArgs(
        type='LoadBalancer',
        selector=labels,
        ports=[ServicePortArgs(port=80)],
    ), opts=ResourceOptions(provider=k8s_provider)
)

# Exportando kubeconfig file
export('kubeconfig', k8s_config)

# Exportando la IP del ingress desplegado
export('ingress_ip', ingress.status.apply(lambda status: status.load_balancer.ingress[0].ip))
