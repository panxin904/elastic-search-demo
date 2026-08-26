---
title: Composite 组合模式
description: 树形结构 + 部分-整体 + 文件系统 / DOM / Kubernetes 资源树
---

# Composite 组合模式

## 核心问题

业务中存在「部分-整体」的层次结构（树 / 森林 / 递归结构），客户端需要**一致对待**「单个对象」和「组合对象」。

**真实场景**：
- 文件系统（文件 / 目录）
- HTML DOM（Node / Element / Document）
- 组织架构（员工 / 部门）
- Kubernetes 资源（Pod / Container）
- 公司股权（个人股东 / 公司股东）

## 核心思想

将对象组合成树形结构，使客户端对单个对象（Leaf）和组合对象（Composite）使用**一致的接口**。

**两种角色**：
- **Component**：定义统一的接口（`operation()` / `add()` / `remove()` / `getChild()`）
- **Leaf**：叶子节点，没有子节点
- **Composite**：容器节点，包含子节点

## 实战：文件系统

```typescript
// 统一接口
interface FileSystemNode {
    getName(): string;
    getSize(): number;
    print(indent: string): void;
}

// 叶子：文件
class File implements FileSystemNode {
    constructor(private name: string, private size: number) {}

    getName() { return this.name; }
    getSize() { return this.size; }
    print(indent: string) {
        console.log(`${indent}📄 ${this.name} (${this.size}B)`);
    }
}

// 容器：目录
class Directory implements FileSystemNode {
    private children: FileSystemNode[] = [];

    constructor(private name: string) {}

    add(node: FileSystemNode) { this.children.push(node); }
    remove(node: FileSystemNode) {
        this.children = this.children.filter(c => c !== node);
    }

    getName() { return this.name; }
    getSize(): number {
        return this.children.reduce((sum, c) => sum + c.getSize(), 0);
    }

    print(indent: string) {
        console.log(`${indent}📁 ${this.name}/`);
        this.children.forEach(c => c.print(indent + '  '));
    }
}

// 客户端：一致对待 file 和 directory
const root = new Directory('project');
const src = new Directory('src');
src.add(new File('index.ts', 1200));
src.add(new File('utils.ts', 800));
root.add(src);
root.add(new File('README.md', 2000));
root.add(new File('package.json', 500));

root.print('');
// 输出：
// 📁 project/
//   📁 src/
//     📄 index.ts (1200B)
//     📄 utils.ts (800B)
//   📄 README.md (2000B)
//   📄 package.json (500B)
```

注意 `getSize()` 是**递归**的（directory 把子节点的 size 累加），客户端不需要知道是 file 还是 directory。

## Java 实战：AWT/Swing

Java AWT/Swing 组件树是 Composite：

```java
// 统一抽象
public abstract class Component {
    public void add(Component c) { /* ... */ }
    public void paint(Graphics g) { /* 子类实现 */ }
}

// 叶子：Button
public class Button extends Component {
    @Override public void paint(Graphics g) { /* 画按钮 */ }
}

// 容器：Panel（可以装其他 Component）
public class Panel extends Component {
    private List<Component> children = new ArrayList<>();

    @Override public void add(Component c) { children.add(c); }

    @Override public void paint(Graphics g) {
        for (Component c : children) {
            c.paint(g);  // 递归绘制
        }
    }
}

// 客户端：随便嵌套
Panel root = new Panel();
Panel leftPanel = new Panel();
leftPanel.add(new Button("OK"));
leftPanel.add(new Button("Cancel"));
root.add(leftPanel);
root.add(new Label("Hello"));

root.paint(graphics);  // 递归绘制所有
```

## 实战：Kubernetes 资源树

Kubernetes 资源天然是树形：

```yaml
# Deployment 包含 ReplicaSet
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: nginx
        # Container 是叶子
        resources:
          requests:
            cpu: 100m
---
# Pod 是容器（Composite）
apiVersion: v1
kind: Pod
metadata:
  name: web-abc123
spec:
  containers:
  - name: app
    image: nginx
  - name: sidecar
    image: istio-proxy
```

`kubectl get` 输出天然是树：

```
Deployment/web
├── ReplicaSet/web-abc
│   ├── Pod/web-abc-xyz1
│   │   ├── Container app
│   │   └── Container istio-proxy
│   ├── Pod/web-abc-xyz2
│   └── Pod/web-abc-xyz3
```

## 组织架构（最经典）

```
CEO
├── CTO
│   ├── 后端团队 Lead
│   │   ├── 后端工程师 A
│   │   └── 后端工程师 B
│   └── 前端团队 Lead
│       ├── 前端工程师 C
│       └── 前端工程师 D
├── CFO
└── COO
```

可以用 Composite 模式：
- `Employee` 抽象（所有员工）
- `IndividualEmployee` 叶子（普通员工）
- `Manager` Composite（持有下属列表）

## 适用边界

✅ **使用场景**：
- 树形 / 递归结构（文件系统 / DOM / 组织架构）
- 客户端需要一致对待「单个」和「组合」
- 业务核心操作可递归（getSize / print / validate）

❌ **避免场景**：
- 结构不是树（用图或其他）
- 叶子 / Composite 行为差异巨大（强行一致接口会很难看）
- 客户端从不需要「穿透」Composite（直接用具体类更简单）

🔄 **变体**：
- **透明 Composite**：Component 接口包含 add/remove（叶子实现抛异常）
- **安全 Composite**：Component 接口只有通用方法，add/remove 在 Composite 子类

💡 **最佳实践**：
- 透明 Composite 更优雅但有 cast 风险
- 安全 Composite 更安全但失去「一致性」优势
- 推荐用透明 + 运行时检查（leaf 不应被 add）
- Java 用 `instanceof` / TS 用 `in` 操作符判断


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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
