---
title: Ansible
---

# Ansible

Ansible 是 Red Hat 推出的配置管理工具，使用 YAML（Playbook）定义任务，agentless 架构（SSH 执行）。

## 一句话总结

> **Ansible = 配置管理 + 轻量部署**。**核心：Playbook（YAML）+ Inventory（主机列表）+ Module（执行单元）**。**强项：agentless / 简单易学 / 适合运维场景**。**弱项：编排能力弱 / 大规模性能差 / 不适合云基础设施**。

---

## 核心模型

```
Inventory     主机列表（IP / 域名 / 分组）
Playbook      YAML 文件，定义任务序列
Role          可复用的 Playbook 集合（tasks / handlers / vars / templates）
Task          单个操作（用 module 执行）
Module        执行单元（apt, copy, service, file, command）
Handler       触发器（notify + listen）
```

## 完整示例

```yaml
# inventory.ini
[web]
web1.example.com
web2.example.com

[db]
db1.example.com

[prod:children]
web
db

# playbook.yml
- name: Deploy web app
  hosts: web
  become: yes
  vars:
    app_version: "1.2.3"
    app_port: 8080

  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
        update_cache: yes

    - name: Copy app config
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/sites-available/app.conf
      notify: reload nginx

    - name: Ensure nginx running
      service:
        name: nginx
        state: started
        enabled: yes

  handlers:
    - name: reload nginx
      service:
        name: nginx
        state: reloaded
```

## Role 结构

```
roles/
└── webserver/
    ├── tasks/main.yml
    ├── handlers/main.yml
    ├── templates/nginx.conf.j2
    ├── files/index.html
    ├── vars/main.yml
    ├── defaults/main.yml
    └── meta/main.yml
```

```yaml
# 使用 role
- hosts: web
  roles:
    - webserver
    - { role: db, when: "inventory_hostname in groups['db']" }
```

## 常用 Module

```yaml
# 包管理
- apt: { name: nginx, state: present }
- yum: { name: httpd, state: latest }
- pip: { name: django, version: "4.2" }

# 文件
- copy: { src: app.conf, dest: /etc/app.conf }
- template: { src: app.conf.j2, dest: /etc/app.conf }
- file: { path: /var/log/app, state: directory, mode: '0755' }

# 服务
- service: { name: nginx, state: started, enabled: yes }

# 命令
- command: /opt/app/bin/migrate
- shell: "ps aux | grep nginx"
```

## 与 Terraform 的边界

| 工具 | 适合 |
|------|------|
| **Terraform** | 云基础设施（VPC / K8s / 托管服务） |
| **Ansible** | OS 配置（包 / 服务 / 文件 / 用户） |
| **混合** | Terraform 创建资源 → Ansible 配置软件 |

## AWX（Ansible Tower）

```yaml
# AWX = Ansible 的 Web UI + REST API
# 功能：
# - Job Template（Web 触发 Playbook）
# - 凭据管理（Vault / SSH key）
# - 审批流
# - 调度（cron）
# - 审计日志
```

## 关联章节

- **02-iac/terraform**：Terraform（云基础设施）
- **02-iac/pulumi**：Pulumi（编程 IaC）
- **01-pipeline/best-practices**：CI 中调用 Ansible

## 一句话总结

> **Ansible = 运维自动化的事实标准**。**何时用：OS 配置 / 批量部署 / 已有 SSH 主机**。**何时不用：云基础设施（用 Terraform）/ 大规模 K8s（用 Helm）/ 复杂编排（用 Ansible + AWX）**。
