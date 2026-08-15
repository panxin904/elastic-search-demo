// cloud-native-html graph data
// 节点分类：docker / k8sarch / workload / service / storage / helm / observability / mesh / cicd / iac / security / serverless / trouble / interview

export const graphData = {
  nodes: [
    // Docker
    { name: 'Docker 基础', category: 'docker', link: '/01-docker/intro', value: 5 },
    { name: '镜像 image', category: 'docker', link: '/01-docker/image', value: 6 },
    { name: '容器 container', category: 'docker', link: '/01-docker/container', value: 6 },
    { name: 'Docker 网络', category: 'docker', link: '/01-docker/network', value: 5 },
    { name: 'Docker 存储 / 卷', category: 'docker', link: '/01-docker/volume', value: 5 },
    { name: 'Docker Compose', category: 'docker', link: '/01-docker/compose', value: 5 },

    // k8s 架构
    { name: 'k8s 是什么', category: 'k8sarch', link: '/02-k8s-arch/overview', value: 5 },
    { name: '控制面 Control Plane', category: 'k8sarch', link: '/02-k8s-arch/control-plane', value: 7 },
    { name: '工作节点 Node', category: 'k8sarch', link: '/02-k8s-arch/node', value: 6 },
    { name: 'kubectl', category: 'k8sarch', link: '/02-k8s-arch/kubectl', value: 6 },
    { name: 'etcd', category: 'k8sarch', link: '/02-k8s-arch/etcd', value: 5 },

    // 工作负载
    { name: 'Pod', category: 'workload', link: '/03-k8s-workload/pod', value: 8 },
    { name: 'Deployment', category: 'workload', link: '/03-k8s-workload/deployment', value: 7 },
    { name: 'StatefulSet', category: 'workload', link: '/03-k8s-workload/statefulset', value: 6 },
    { name: 'DaemonSet', category: 'workload', link: '/03-k8s-workload/daemonset', value: 5 },
    { name: 'Job / CronJob', category: 'workload', link: '/03-k8s-workload/job', value: 5 },

    // Service / 网络
    { name: 'Service', category: 'service', link: '/04-k8s-service/service', value: 7 },
    { name: 'Ingress', category: 'service', link: '/04-k8s-service/ingress', value: 6 },
    { name: 'NetworkPolicy', category: 'service', link: '/04-k8s-service/network-policy', value: 5 },

    // 存储
    { name: 'PV / PVC', category: 'storage', link: '/05-k8s-storage/pv-pvc', value: 6 },
    { name: 'StorageClass', category: 'storage', link: '/05-k8s-storage/storageclass', value: 5 },
    { name: 'ConfigMap / Secret', category: 'storage', link: '/05-k8s-storage/configmap-secret', value: 6 },

    // Helm
    { name: 'Helm Chart', category: 'helm', link: '/06-helm/chart', value: 6 },
    { name: 'template / values', category: 'helm', link: '/06-helm/template', value: 6 },
    { name: 'Chart 仓库', category: 'helm', link: '/06-helm/repository', value: 5 },

    // 可观测
    { name: 'Prometheus', category: 'observability', link: '/07-observability/prometheus', value: 7 },
    { name: 'Grafana', category: 'observability', link: '/07-observability/grafana', value: 6 },
    { name: 'Loki', category: 'observability', link: '/07-observability/loki', value: 5 },
    { name: 'Alertmanager', category: 'observability', link: '/07-observability/alertmanager', value: 5 },

    // Service Mesh
    { name: 'Istio', category: 'mesh', link: '/08-service-mesh/istio', value: 7 },
    { name: 'Sidecar', category: 'mesh', link: '/08-service-mesh/sidecar', value: 5 },
    { name: '流量管理', category: 'mesh', link: '/08-service-mesh/traffic', value: 5 },

    // CI/CD
    { name: 'GitOps', category: 'cicd', link: '/09-cicd/gitops', value: 5 },
    { name: 'ArgoCD', category: 'cicd', link: '/09-cicd/argocd', value: 6 },
    { name: 'Tekton / JenkinsX', category: 'cicd', link: '/09-cicd/tekton', value: 5 },

    // IaC
    { name: 'Terraform', category: 'iac', link: '/10-iac/terraform', value: 6 },
    { name: 'Pulumi', category: 'iac', link: '/10-iac/pulumi', value: 4 },
    { name: 'Helmfile / Kustomize', category: 'iac', link: '/10-iac/helmfile', value: 5 },

    // 安全
    { name: 'RBAC', category: 'security', link: '/11-security/rbac', value: 6 },
    { name: 'Secret 管理', category: 'security', link: '/11-security/secret', value: 5 },
    { name: 'NetworkPolicy + PodSecurity', category: 'security', link: '/11-security/policy', value: 5 },
    { name: 'Falco', category: 'security', link: '/11-security/falco', value: 4 },

    // Serverless
    { name: 'Knative', category: 'serverless', link: '/12-serverless/knative', value: 5 },
    { name: 'Lambda / Cloud Run', category: 'serverless', link: '/12-serverless/managed', value: 4 },

    // 排错
    { name: 'kubectl debug', category: 'trouble', link: '/13-troubleshooting/debug', value: 5 },
    { name: 'Pod 卡死', category: 'trouble', link: '/13-troubleshooting/pod-trouble', value: 5 },
    { name: '网络 / DNS 排错', category: 'trouble', link: '/13-troubleshooting/network', value: 5 },

    // 面试
    { name: 'CKA 考试', category: 'interview', link: '/14-interview/cka', value: 6 },
    { name: 'CKS 安全', category: 'interview', link: '/14-interview/cks', value: 5 },
    { name: '高频面试题', category: 'interview', link: '/14-interview/questions', value: 5 }
  ],

  links: [
    // Docker → k8s
    { source: 'Docker 基础', target: 'k8s 是什么' },
    { source: 'Docker 镜像 image', target: 'k8s 是什么' },
    { source: 'Docker 容器 container', target: 'Pod' },
    { source: 'Docker 容器 container', target: 'k8s 是什么' },
    { source: 'Docker Compose', target: 'k8s 是什么' },

    // k8s 架构 → workload
    { source: 'k8s 是什么', target: '控制面 Control Plane' },
    { source: '控制面 Control Plane', target: '工作节点 Node' },
    { source: '控制面 Control Plane', target: 'etcd' },
    { source: '工作节点 Node', target: 'Pod' },
    { source: 'kubectl', target: 'Pod' },

    // Pod → workload 类型
    { source: 'Pod', target: 'Deployment' },
    { source: 'Pod', target: 'StatefulSet' },
    { source: 'Pod', target: 'DaemonSet' },
    { source: 'Pod', target: 'Job / CronJob' },

    // workload → service
    { source: 'Deployment', target: 'Service' },
    { source: 'StatefulSet', target: 'Service' },
    { source: 'Service', target: 'Ingress' },
    { source: 'Service', target: 'NetworkPolicy' },

    // 存储
    { source: 'Pod', target: 'PV / PVC' },
    { source: 'PV / PVC', target: 'StorageClass' },
    { source: 'Pod', target: 'ConfigMap / Secret' },
    { source: 'ConfigMap / Secret', target: 'Secret 管理' },

    // Helm
    { source: 'kubectl', target: 'Helm Chart' },
    { source: 'Helm Chart', target: 'template / values' },
    { source: 'Helm Chart', target: 'Chart 仓库' },
    { source: 'Helm Chart', target: 'kubectl' },

    // 可观测
    { source: 'Service', target: 'Prometheus' },
    { source: 'Pod', target: 'Prometheus' },
    { source: 'Prometheus', target: 'Grafana' },
    { source: 'Prometheus', target: 'Alertmanager' },
    { source: 'Pod', target: 'Loki' },
    { source: 'Loki', target: 'Grafana' },

    // Mesh
    { source: 'Service', target: 'Istio' },
    { source: 'Istio', target: 'Sidecar' },
    { source: 'Istio', target: '流量管理' },

    // CI/CD
    { source: 'Helm Chart', target: 'ArgoCD' },
    { source: 'ArgoCD', target: 'GitOps' },
    { source: 'Helm Chart', target: 'Tekton / JenkinsX' },
    { source: 'GitOps', target: 'Tekton / JenkinsX' },

    // IaC
    { source: 'Helm Chart', target: 'Helmfile / Kustomize' },
    { source: 'Helmfile / Kustomize', target: 'Terraform' },
    { source: 'Terraform', target: 'Pulumi' },

    // 安全
    { source: 'kubectl', target: 'RBAC' },
    { source: 'ConfigMap / Secret', target: 'Secret 管理' },
    { source: 'NetworkPolicy', target: 'NetworkPolicy + PodSecurity' },
    { source: 'Pod', target: 'Falco' },

    // Serverless
    { source: 'k8s 是什么', target: 'Knative' },
    { source: 'Knative', target: 'Lambda / Cloud Run' },
    { source: 'Service', target: 'Lambda / Cloud Run' },

    // 排错
    { source: 'kubectl', target: 'kubectl debug' },
    { source: 'Pod', target: 'Pod 卡死' },
    { source: 'Service', target: '网络 / DNS 排错' },
    { source: 'kubectl debug', target: 'Pod 卡死' },

    // 面试
    { source: 'k8s 是什么', target: 'CKA 考试' },
    { source: 'RBAC', target: 'CKS 安全' },
    { source: 'CKA 考试', target: '高频面试题' },
    { source: 'CKS 安全', target: '高频面试题' },

    // 跨链
    { source: 'Helm Chart', target: 'ConfigMap / Secret' },
    { source: 'Ingress', target: 'NetworkPolicy' },
    { source: 'Service Mesh', target: 'Istio' },
    { source: 'Service', target: 'Service Mesh' },
    { source: 'Falco', target: 'Secret 管理' },
    { source: 'Ingress', target: 'Cert-manager' }
  ]
}