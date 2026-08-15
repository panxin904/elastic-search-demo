---
title: Jenkins
---

# Jenkins

Jenkins 是 CI/CD 工具的鼻祖（2004 年 Hudson 衍生），功能最全面但运维最重。本章梳理 Jenkins 核心架构与现代化用法。

## 一句话总结

> **Jenkins = 经典 CI/CD 工具**。**强项：插件生态最丰富 / Pipeline as Code / 分布式 Master-Agent**。**弱项：运维重 / UI 老旧 / 配置漂移（解决：Configuration as Code）**。

---

## 架构

```
Jenkins Master（控制器）
  ├── 调度 job
  ├── 存储配置 / build 历史 / plugins
  └── 不执行 build（避免 master 资源竞争）

Jenkins Agent（执行器）
  ├── SSH / JNLP / K8s Pod 启动
  ├── 接收 job 执行
  └── 并发能力（多个 agent）
```

## Jenkinsfile（Pipeline as Code）

```groovy
pipeline {
    agent any

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        timestamps()
    }

    stages {
        stage('Build') {
            steps {
                sh 'npm ci'
                sh 'npm run build'
            }
        }

        stage('Test') {
            parallel {
                stage('Unit') {
                    steps { sh 'npm test' }
                }
                stage('Integration') {
                    steps { sh 'npm run test:e2e' }
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                input 'Deploy to production?'
                sh 'kubectl apply -f k8s/'
            }
        }
    }

    post {
        success { slackSend(channel: '#deploys', message: '✅ Deployed') }
        failure { slackSend(channel: '#alerts', message: '❌ Failed') }
    }
}
```

## K8s 上的 Jenkins（动态 Agent）

```yaml
# jenkins-casc.yaml（Configuration as Code）
jenkins:
  clouds:
    - kubernetes:
        name: "k8s"
        serverUrl: "https://k8s-api.example.com"
        namespace: "jenkins"
        templates:
          - name: "jenkins-agent"
            label: "jenkins-agent"
            containerTemplate:
              name: "jnlp"
              image: "jenkins/inbound-agent:latest"
```

```groovy
// Jenkinsfile 中动态使用 K8s Agent
pipeline {
    agent {
        kubernetes {
            label 'jenkins-agent'
            yaml '''
                apiVersion: v1
                kind: Pod
                spec:
                  containers:
                    - name: jnlp
                      image: jenkins/inbound-agent
                    - name: node
                      image: node:20
                      command: ["cat"]
                      tty: true
                '''
        }
    }
    stages {
        stage('Test') {
            steps {
                container('node') {
                    sh 'npm ci && npm test'
                }
            }
        }
    }
}
```

## Configuration as Code（JCasC）

```yaml
# jenkins.yaml（声明式配置，避免 UI 配置漂移）
jenkins:
  systemMessage: "Production Jenkins"
  numExecutors: 0
  securityRealm:
    local:
      allowsSignup: false
  authorizationStrategy:
    loggedInUsersCanDoAnything:
      allowAnonymousRead: false

credentials:
  system:
    domainCredentials:
      - credentials:
          - usernamePassword:
              scope: GLOBAL
              id: "github-creds"
              username: "ci-bot"
              password: "${GITHUB_TOKEN}"
```

## 插件管理

```yaml
# plugins.yaml（声明式插件列表）
plugins:
  required:
    - kubernetes:4260.va7866468c5b_d
    - configuration-as-code:1850.va_a_8c31d99e1
    - pipeline-stage-view:2.34
    - blueocean:1.27.7
```

## 关联章节

- **01-pipeline/github-actions**：GitHub Actions 对比（云原生 vs 老牌）
- **01-pipeline/tekton**：Tekton（更云原生的 Pipeline 框架）
- **06-best-practices/caching**：Jenkins 缓存策略

## 一句话总结

> **Jenkins = 复杂场景的常青树**。**核心价值：插件 1800+ / JCasC 解决配置漂移 / K8s 动态 agent**。**何时不用：SaaS 优先 / 团队小 / 追求现代化 UI**。
