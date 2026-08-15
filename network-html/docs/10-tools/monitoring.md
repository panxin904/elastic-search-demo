---
title: 网络监控
---

# 网络监控

<div class="nt-badge nt-badge-tools">监控</div>
<div class="nt-badge nt-badge-cloud">运维</div>

网络监控是保障服务稳定性的关键，本章梳理常用监控工具、指标、可视化方案。

## 1. 监控维度

| 维度 | 指标 |
| --- | --- |
| 设备 | CPU、内存、温度、电源、风扇 |
| 接口 | 带宽、错包、丢包、CRC |
| 协议 | TCP 重传、UDP 丢包、ICMP 时延 |
| 应用 | HTTP QPS、延迟、错误率 |
| 业务 | 转化率、订单数 |

## 2. 主流工具

| 工具 | 用途 |
| --- | --- |
| Zabbix | 综合监控 |
| Prometheus + Grafana | 时序监控 |
| LibreNMS | 网络设备 |
| PRTG | 商业 |
| SolarWinds | 商业 |
| Cacti | 历史流量 |
| smokeping | 长期时延 |
| ntopng | 流量分析 |
| iftop / nethogs | 实时流量 |
| vnStat | 历史流量 |

## 3. SNMP

简单网络管理协议，设备主动暴露指标。

```bash
# 安装 snmp 工具
apt install snmp

# 查询
snmpwalk -v2c -c public 192.168.1.1
snmpget -v2c -c public 192.168.1.1 .1.3.6.1.2.1.2.2.1.10.1
```

常见 OID：

| OID | 含义 |
| --- | --- |
| 1.3.6.1.2.1.2.2.1.10 | 接口入字节数 |
| 1.3.6.1.2.1.2.2.1.16 | 接口出字节数 |
| 1.3.6.1.2.1.2.2.1.14 | 入错包 |
| 1.3.6.1.2.1.1.3 | 设备运行时间 |
| 1.3.6.1.4.1.9.9.109 | Cisco CPU |

## 4. NetFlow / sFlow / IPFIX

| 协议 | 厂商 | 描述 |
| --- | --- | --- |
| NetFlow | Cisco | 主流 |
| sFlow | 通用 | 采样 |
| IPFIX | IETF | NetFlow 标准化 |

采集器：

- nfdump + nfsen
- goflow2
- FastNetMon

## 5. Prometheus 监控

### 5.1 核心架构

```
Exporter → Prometheus Server → Alertmanager / Grafana
```

### 5.2 常用 Exporter

| Exporter | 用途 |
| --- | --- |
| node_exporter | 主机（CPU、内存、网卡） |
| blackbox_exporter | 黑盒（HTTP/TCP/ICMP） |
| snmp_exporter | SNMP |
| mysqld_exporter | MySQL |
| nginx_exporter | Nginx |
| cadvisor | 容器 |
| pushgateway | 短任务 |

### 5.3 关键指标

```yaml
# HTTP 探活
probe_http_status_code
probe_duration_seconds

# TCP
probe_success
probe_failed_due_to_regex

# ICMP
probe_icmp_duration_seconds
```

### 5.4 告警规则

```yaml
groups:
- name: network
  rules:
  - alert: HighPacketLoss
    expr: rate(node_network_mtu_err_total[5m]) > 10
    for: 2m
    annotations:
      summary: "Packet errors > 10/s on {{ $labels.instance }}"

  - alert: HighLatency
    expr: probe_duration_seconds > 1
    for: 5m
    annotations:
      summary: "Probe to {{ $labels.instance }} > 1s"
```

## 6. Grafana 仪表盘

| Dashboard | 用途 |
| --- | --- |
| Node Exporter Full | 主机全指标 |
| Prometheus 2.0 Stats | 自身状态 |
| Blackbox Exporter | 探活 |
| SNMP | 网络设备 |
| Nginx | Web |

## 7. 时延监控

```bash
# 长期 ping
ping -i 60 host > /var/log/ping.log &

# smokeping
apt install smokeping
# 配置 /etc/smokeping/config.d/Targets
```

```ini
+ myhost
menu = My Host
title = My Host
host = 8.8.8.8
```

## 8. 链路监控

| 工具 | 用途 |
| --- | --- |
| mtr | 路径 + 丢包 |
| smokeping | 长期时延 |
| NLTM | 多目标 |
| PingPlotter | Windows 友好 |

## 9. 流量分析

```bash
# iftop
iftop -i eth0 -n

# nethogs（按进程）
nethogs eth0

# ntopng（Web）
ntopng -i eth0
```

## 10. 日志收集

```
设备 → syslog → rsyslog → Kafka → ES → Kibana
```

常见日志：

| 日志 | 来源 |
| --- | --- |
| Access Log | Nginx / Apache |
| Error Log | 应用 / 系统 |
| Firewall Log | iptables / WAF |
| Flow Log | VPC / 交换机 |
| Audit Log | 堡垒机 / SIEM |

## 11. DNS 监控

```bash
# 解析成功率
dig @8.8.8.8 example.com +short | head

# 延迟
dig example.com | grep "Query time"
```

Prometheus + blackbox_exporter：

```yaml
- job_name: dns
  metrics_path: /probe
  params:
    module: [dns]
  static_configs:
  - targets: [8.8.8.8:53, 1.1.1.1:53]
```

## 12. 告警策略

| 告警 | 阈值 |
| --- | --- |
| 接口带宽 > 80% | 5m |
| 接口错包 > 10/s | 5m |
| HTTP 5xx > 1% | 5m |
| DNS 解析失败 | 立即 |
| TCP 重传率 > 1% | 5m |
| 证书 30 天内到期 | 每日 |

## 13. 常见面试题

1. **SNMP 端口？** 161（查询）/ 162（trap）。
2. **Prometheus 拉还是推？** 拉模式（pull）。
3. **NetFlow vs sFlow？** NetFlow 全量，sFlow 采样。
4. **blackbox_exporter 干啥？** 黑盒探活（HTTP/TCP/ICMP/DNS）。
5. **怎么监控丢包？** netstat -s 看 Retrans / ifconfig errors。
6. **告警如何降噪？** 抑制、分组、合并相似告警、临时静默。
