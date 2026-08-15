---
title: VPC 虚拟私有云
---

# VPC 虚拟私有云

<div class="nt-badge nt-badge-cloud">云网络</div>
<div class="nt-badge nt-badge-network">核心</div>

VPC（Virtual Private Cloud）是公有云中**逻辑隔离**的网络空间，用户可在 VPC 内自由规划网段、路由、网关、安全策略，是云上网络的基础。

## 1. VPC 核心概念

| 概念 | 说明 |
| --- | --- |
| VPC | 虚拟私有云（一个隔离网络） |
| Subnet | 子网（可用区 / CIDR） |
| Route Table | 路由表 |
| Internet Gateway | 公网网关（IGW） |
| NAT Gateway | SNAT 出口 |
| EIP | 弹性公网 IP |
| Security Group | 安全组（实例级防火墙） |
| NACL | 网络 ACL（子网级防火墙） |
| VPC Peering | VPC 对等连接 |
| Transit Gateway | 中转网关 |
| PrivateLink | 私网访问服务 |
| VPN Connection | 加密隧道 |
| Direct Connect | 专线 |

## 2. 网段规划

| 云厂商 | 默认建议 |
| --- | --- |
| AWS | 10.0.0.0/16 |
| Azure | 10.0.0.0/16 |
| 阿里云 | 192.168.0.0/16 |
| 腾讯云 | 10.0.0.0/16 |
| GCP | 10.0.0.0/16 |

经典企业网段：

```
生产-VPC:  10.0.0.0/16
   ├── prod-web:  10.0.1.0/24 (AZ1)
   ├── prod-app:  10.0.2.0/24 (AZ1)
   └── prod-db:   10.0.3.0/24 (AZ1, 私有子网)

测试-VPC:  10.1.0.0/16
   ├── test-web:  10.1.1.0/24
   └── test-db:   10.1.2.0/24

办公-VPC:  10.2.0.0/16
```

## 3. 路由表

```
Destination        Target
10.0.0.0/16        local              ← VPC 内部
0.0.0.0/0          igw-xxx            ← 走公网
0.0.0.0/0          nat-xxx            ← 走 NAT
10.1.0.0/16        pcx-xxx            ← 走对等连接
```

## 4. 安全组 vs NACL

| 维度 | Security Group | NACL |
| --- | --- | --- |
| 作用对象 | 实例（ENI） | 子网 |
| 状态 | 有状态 | 无状态（需双向） |
| 规则 | Allow 默认 | Allow / Deny |
| 优先级 | 顺序评估 | 数字越小越高 |
| 适用 | 主机防火墙 | 子网边界 |

## 5. 互联网访问

### 5.1 公网入站

```
Internet ──> IGW ──> Route Table ──> 公有子网 ──> 实例
                                       (需要 EIP/Public IP)
```

### 5.2 私有子网出网

```
私有子网实例 ──> Route Table ──> NAT Gateway ──> IGW ──> Internet
```

私有子网**无** EIP，必须经 NAT 才能主动出公网。

## 6. VPC 互联

| 方案 | 适用 |
| --- | --- |
| VPC Peering | 2 个 VPC 全网互通 |
| Transit Gateway | 多 VPC 中心辐射 |
| PrivateLink | 私网访问服务 |
| VPC Share | 多账号共享 |
| SDX（Software Defined Interconnect） | 多云互联 |
| TGW + RAM | 多账号 |

```
VPC-A ─┐
VPC-B ─┼─ Transit Gateway ── On-Premise
VPC-C ─┘
```

## 7. 混合云

### 7.1 VPN 连接

```
On-Prem ──[IPsec VPN]──> VGW ──> VPC
```

- 走公网
- 部署快、带宽受限
- 加密传输

### 7.2 专线（Direct Connect）

```
On-Prem ──[光纤]──> DX 端口 ──> DX Location ──> 区域接入点 ──> VPC
```

- 物理专线，稳定低时延
- 成本高、开通慢
- 可双线主备

## 8. 多账号 + 多 VPC

```
Master Account
  ├── prod-account
  ├── dev-account
  └── data-account

每个账号独立 VPC，TGW 中心互联
```

## 9. 跨区域

| 方案 | 描述 |
| --- | --- |
| Peering | 同区域 |
| TGW Peering | 跨区域 |
| Inter-Region Peering | 跨区域对等 |
| Cloud WAN | 全球骨干 |
| 流量镜像 | 跨区域同步 |

## 10. IPv6

- 大多云厂商支持 VPC IPv6
- 双栈：IPv4 + IPv6
- NAT64 / DNS64 访问 IPv4 资源

## 11. 实战配置

### AWS CLI 创建 VPC

```bash
aws ec2 create-vpc --cidr-block 10.0.0.0/16
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --vpc-id vpc-xxx --internet-gateway-id igw-xxx
aws ec2 create-route --route-table-id rtb-xxx \
  --destination-cidr-block 0.0.0.0/0 --gateway-id igw-xxx
```

### Terraform

```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = { Name = "prod-vpc" }
}
```

## 12. 常见面试题

1. **VPC 是什么？** 公有云中逻辑隔离的虚拟网络。
2. **公有子网 vs 私有子网？** 公有可直连 IGW，私有需经 NAT。
3. **安全组 vs NACL？** 实例级 vs 子网级，状态化 vs 无状态。
4. **VPC Peering 限制？** 1 对 1，不支持传递。
5. **Transit Gateway 作用？** 多 VPC 中心互联。
6. **VPN vs 专线？** VPN 走公网，便宜；专线走物理光纤，稳定。
