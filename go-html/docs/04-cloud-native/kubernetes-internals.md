---
title: Kubernetes 源码导读
---

# Kubernetes 源码导读

**Kubernetes（K8s）= Go 写的事实标准**——100+ 个组件，全是 Go。

## 一句话总结

> **K8s = kube-apiserver + kube-scheduler + kube-controller-manager + kubelet + kube-proxy + etcd**。**所有组件用 client-go 通信**。

---

## 一、K8s 架构全景

```
                    ┌──────────────┐
                    │ kubectl/UI   │
                    └──────┬───────┘
                           │ HTTPS
                    ┌──────▼───────┐
                    │ kube-apiserver │ ← 唯一入口
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼─────┐      ┌────▼─────┐      ┌────▼─────┐
   │scheduler │      │controller│      │  etcd    │
   │          │      │ manager  │      │ (存储)   │
   └──────────┘      └──────────┘      └──────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐         ┌───▼───┐         ┌───▼───┐
   │ kubelet │         │kubelet│         │kubelet│
   │ (Node1) │         │(Node2)│         │(Node3)│
   └─────────┘         └───────┘         └───────┘
```

## 二、源码结构

```bash
git clone https://github.com/kubernetes/kubernetes
cd kubernetes

ls cmd/                  # 组件入口
  kube-apiserver/
  kube-scheduler/
  kube-controller-manager/
  kubelet/

ls pkg/                  # 核心库
  api/                   # API types
  apis/                  # API 组
  client/                # 客户端
  registry/              # 注册表
  controller/            # controller 框架
  scheduler/             # 调度器
  kubelet/               # kubelet
  kube-proxy/            # 网络代理

ls staging/              # 独立模块
  src/k8s.io/api/
  src/k8s.io/client-go/
  src/k8s.io/apimachinery/
```

**Go monorepo 模式**：`staging/src/k8s.io/*` 是 vendored 子模块。

## 三、API Server 核心

```go
// cmd/kube-apiserver/apiserver.go
func Run(completeOptions completedServerRunOptions, stopCh <-chan struct{}) error {
    server, err := CreateServerChain(completeOptions, stopCh)
    if err != nil { return err }
    
    return server.PrepareRun().Run(stopCh)
}

// 三大核心：
// 1. GenericAPIServer：HTTP + 认证 + 鉴权
// 2. Aggregator：CRD 聚合
// 3. APIExtensions：CRD 注册
```

**请求处理链**：
1. Authentication（认证）
2. Authorization（RBAC）
3. Admission（mutating/validating webhook）
4. Validation
5. Etcd 读写
6. 返回

## 四、Scheduler 调度器

```go
// pkg/scheduler/scheduler.go
type Scheduler struct {
    Algorithm    ScheduleAlgorithm
    Extenders    []SchedulerExtender
    Error       func(*Pod, error)
    Recorder     events.EventRecorder
    NextPod      func() *Pod
    WaitForCacheSync func() bool
}

func (sched *Scheduler) scheduleOne() {
    pod := sched.NextPod()
    suggestedHost, err := sched.Algorithm.Schedule(pod)
    if err != nil {
        // 抢占
        sched.preempt(pod)
        return
    }
    // 假定 (assume) 缓存
    sched.assume(assumedPod)
    // 异步 bind
    go sched.bind(assumedPod, suggestedHost)
}
```

**调度框架**（Scheduling Framework）：
- **PreFilter**：前置过滤
- **Filter**：节点过滤（资源/亲和性/污点）
- **Score**：打分
- **Reserve**：预留
- **Permit**：批准
- **PreBind**：绑定前
- **Bind**：执行绑定
- **PostBind**：绑定后

## 五、Controller Manager

```go
// pkg/controller/
type ReplicaSetController struct {
    rsControl  rsControlInterface
    podControl controller.PodControlInterface
    expectations *expectations
}

func (rsc *ReplicaSetController) processNextWorkItem() bool {
    key, _ := rsc.queue.Get()
    rsc.syncReplicaSet(key.(string))
    return true
}

func (rsc *ReplicaSetController) syncReplicaSet(key string) error {
    namespace, name := cache.SplitMetaNamespaceKey(key)
    rs, _ := rsc.rsLister.ReplicaSets(namespace).Get(name)
    // 计算当前 vs 期望
    // 调 rsc.podControl 创建/删除 pod
    // 更新 status
}
```

**workqueue 模式**：
- Informer 监听 watch 事件
- 加入 workqueue
- worker goroutine 消费
- 失败 requeue（指数退避）

## 六、client-go — 编程接口

```go
import "k8s.io/client-go/kubernetes"
import "k8s.io/client-go/tools/clientcmd"

config, _ := clientcmd.BuildConfigFromFlags("", "/path/to/kubeconfig")
clientset, _ := kubernetes.NewForConfig(config)

// List pods
pods, _ := clientset.CoreV1().Pods("default").List(ctx, metav1.ListOptions{})

// Create deployment
deployment := &appsv1.Deployment{
    ObjectMeta: metav1.ObjectMeta{Name: "nginx"},
    Spec: appsv1.DeploymentSpec{
        Replicas: int32Ptr(3),
        Selector: &metav1.LabelSelector{MatchLabels: map[string]string{"app": "nginx"}},
        Template: corev1.PodTemplateSpec{
            ObjectMeta: metav1.ObjectMeta{Labels: map[string]string{"app": "nginx"}},
            Spec: corev1.PodSpec{Containers: []corev1.Container{{Name: "nginx", Image: "nginx:1.25"}}},
        },
    },
}
clientset.AppsV1().Deployments("default").Create(ctx, deployment, metav1.CreateOptions{})
```

## 七、Informer / Watch 机制

```go
factory := informers.NewSharedInformerFactory(clientset, 30*time.Second)
podInformer := factory.Core().V1().Pods().Informer()

podInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
    AddFunc: func(obj interface{}) { /* 新 pod 加入 */ },
    UpdateFunc: func(old, new interface{}) { /* pod 更新 */ },
    DeleteFunc: func(obj interface{}) { /* pod 删除 */ },
})

factory.Start(stopCh)
factory.WaitForCacheSync(stopCh)
```

**Informer 三件套**：
1. **Reflector**：list+watch apiserver
2. **DeltaFIFO**：事件队列
3. **Indexer**：本地缓存（thread-safe）

## 八、CRD + Controller Runtime

**自定义资源**：

```go
// 定义 CRD
type MyApp struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec   MyAppSpec   `json:"spec,omitempty"`
    Status MyAppStatus `json:"status,omitempty"`
}

type MyAppSpec struct {
    Replicas int    `json:"replicas"`
    Image    string `json:"image"`
}

// 实现 DeepCopyObject
func (m *MyApp) DeepCopyObject() runtime.Object { /* ... */ }

// 注册到 Scheme
scheme.AddKnownTypes(MyAppGroupVersion, &MyApp{}, &MyAppList{})
```

**controller-runtime**（Kubebuilder）：

```go
func (r *MyAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var myapp myappv1.MyApp
    if err := r.Get(ctx, req.NamespacedName, &myapp); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    
    // 调谐逻辑：保证 Spec.Status == Spec.Replicas
    if myapp.Status.Replicas != myapp.Spec.Replicas {
        // 创建/删除 pod
    }
    return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
}
```

## 九、kubelet 核心

```go
// pkg/kubelet/kubelet.go
type Kubelet struct {
    hostname      string
    nodeName      string
    containerRuntime  kubecontainer.Runtime
    imageManager  kubeimage.Manager
    cadvisor      cadvisor.Interface
    oomWatcher    oomwatcher.Watcher
}

func (kl *Kubelet) syncPod(o syncPodOptions) error {
    // 1. 创建 sandbox（gVisor / runc）
    // 2. 启动 containers
    // 3. 设置网络
    // 4. health check (probe)
    // 5. 报告 status 给 apiserver
}
```

**CRI（Container Runtime Interface）**：
- gRPC 接口
- kubelet 调 cri，cri 调 runc / containerd

## 十、Go 的优势在 K8s

| 优势 | 体现 |
|---|---|
| 静态二进制 | kubelet / kube-proxy 几 MB，无需 runtime |
| goroutine | controller 并发处理上千对象 |
| channel | Informer 事件流 |
| interface | storage provider 抽象（etcd / 未来 sqlite） |
| gofmt | K8s 100+ 仓库风格统一 |
| go mod | 统一依赖管理 |

## 关联章节

- **04-cloud-native/docker-internals**：容器基础
- **04-cloud-native/etcd-internals**：K8s 后端存储
- **04-cloud-native/cncf-ecosystem**：CNCF 全景

## 一句话总结

> **K8s 源码 = 100+ 组件 + client-go + controller-runtime**。**Go 让大规模集群管理代码保持简洁**。


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
