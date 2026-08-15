---
title: 风控系统
---
# 风控系统

## 1. 是什么

风控 = 风险管理。识别 + 评估 + 应对风险。

应用场景：
  - 支付反欺诈
  - 信贷风控
  - 账号安全
  - 反爬虫
  - 内容审核

## 2. 风控架构

```
请求 → 实时拦截（规则 + 模型）
  ↓
离线分析 → 风险标签
  ↓
决策引擎（拒绝 / 通过 / 人工）
```

## 3. 实时风控

### 3.1 规则引擎（Drools）

```java
// 规则：1 分钟内 5 次登录失败 → 锁定
rule "Too Many Failed Logins"
  when
    $event: LoginEvent(status == "FAILED")
    Number($count: intValue >= 5) from accumulate(
      $e: LoginEvent(userId == $event.userId, status == "FAILED", this != $event) over window:time(1m),
      count($e)
    )
  then
    $event.setAction("LOCK");
    insert(new RiskAction($event.userId, "LOCK"));
end
```

### 3.2 模型评分（XGBoost）

```python
import xgboost as xgb

# 特征
features = ['user_age', 'account_age_days', 'login_count_1h',
            'device_fp', 'ip_country', 'behavior_score', ...]

# 训练
dtrain = xgb.DMatrix(X_train, label=y_train)
params = {'objective': 'binary:logistic', 'max_depth': 6}
model = xgb.train(params, dtrain, num_boost_round=100)

# 预测
dtest = xgb.DMatrix(X_test)
risk_score = model.predict(dtest)  # 0-1 风险分数
```

### 3.3 决策引擎

```java
// 决策
if (risk_score > 0.9) {
  return REJECT;  // 高风险拒绝
} else if (risk_score > 0.6) {
  return MANUAL_REVIEW;  // 中风险人工
} else {
  return PASS;  // 低风险通过
}
```

## 4. 风控特征

### 4.1 设备指纹

```sql
-- 设备指纹 = device_id + 浏览器指纹 + IP + GPS
CREATE TABLE device_fp (
  user_id BIGINT,
  device_id STRING,
  browser_fp STRING,
  ip STRING,
  gps_lat DOUBLE,
  gps_lng DOUBLE,
  ts TIMESTAMP
);

-- 查询：1 设备多账号（异常）
SELECT device_id, COUNT(DISTINCT user_id) AS user_cnt
FROM device_fp
WHERE ts > NOW() - INTERVAL 1 DAY
GROUP BY device_id
HAVING user_cnt > 5;
```

### 4.2 行为模式

```sql
-- 用户行为序列
CREATE TABLE user_behavior (
  user_id BIGINT,
  behavior STRING,
  ts TIMESTAMP
);

-- 异常行为：凌晨大量下单
SELECT user_id, COUNT(*) AS order_cnt
FROM user_behavior
WHERE behavior = 'order'
  AND HOUR(ts) BETWEEN 0 AND 5
  AND ts > NOW() - INTERVAL 1 DAY
GROUP BY user_id
HAVING order_cnt > 10;
```

### 4.3 关联图

```sql
-- 用户 - 设备 - IP - 收货地址 关联图
SELECT user_id, device_id, ip, address_id
FROM user_login
WHERE ts > NOW() - INTERVAL 7 DAY;

-- 团伙识别：共享设备 / IP / 收货地址
```

## 5. 风控案例

### 5.1 支付反欺诈

```
实时特征：
  - 设备指纹
  - 行为序列（点击 + 下单 + 支付）
  - 金额 / 频次
  - GPS / IP

模型：
  - XGBoost（特征工程）
  - 深度学习（序列模型）

决策：
  - 通过 / 二次验证 / 拒绝
```

### 5.2 信贷风控

```
贷前：
  - 身份核验
  - 信用评分（芝麻信用）
  - 反欺诈评分

贷中：
  - 行为监控
  - 还款能力评估

贷后：
  - 催收策略
  - 不良资产管理
```

### 5.3 反爬虫

```
规则：
  - IP 频次（> 100 次 / 分钟）
  - UA 异常（无 UA / 异常 UA）
  - 行为异常（无 mouse / 直接访问 API）
  - 验证码触发

决策：
  - 验证码
  - IP 封禁
  - 限速
```

## 6. 实战架构

```
请求 → Nginx（限流）
  ↓
风控引擎（规则 + 模型）
  ↓
  ├─ 通过
  ├─ 拒绝
  └─ 二次验证
  
离线：
  标签 → 训练（XGBoost / 深度学习）
  特征 → 监控
```

## 7. 实战技术栈

| 层级 | 技术 |
|------|------|
| 规则 | Drools / Aviator / Easy Rules |
| 模型 | XGBoost / TensorFlow / PyTorch |
| 特征 | Flink / Spark / Hive / Doris |
| 决策 | 自研 / Drools |
| 监控 | Grafana / Prometheus |

## 8. 实战评估指标

| 指标 | 含义 |
|------|------|
| 召回率 | 命中风险 / 总风险 |
| 误报率 | 误杀 / 总拒绝 |
| 覆盖率 | 策略覆盖交易比例 |
| 损失金额 | 风控拦截金额 |

## 9. 实战 checklist

- [ ] 规则引擎（Drools）
- [ ] 模型训练（XGBoost / 深度学习）
- [ ] 实时特征（Flink）
- [ ] 决策引擎（拒绝 / 通过 / 人工）
- [ ] 评估指标（召回率 / 误报率）
- [ ] A / B 测试
- [ ] 监控（实时）

## 10. 实战建议

1. **规则 + 模型**：规则拦截已知 + 模型识别未知
2. **特征工程**：行为 + 设备 + 关联
3. **实时 + 离线**：实时拦截 + 离线分析
4. **决策引擎**：灵活配置
5. **监控**：实时监控 + 离线评估

## 🔗 下一步
- [用户画像](/13-cases/user-profile)
- [推荐系统](/13-cases/recommendation)
- [实时数仓](/10-data-lake/lakehouse)
