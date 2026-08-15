<template>
  <div class="mindmap-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="mm-toolbar">
      <button class="mm-toolbar__btn" @click="expandAll">📖 全部展开</button>
      <button class="mm-toolbar__btn" @click="collapseAll">📕 全部收起</button>
      <button class="mm-toolbar__btn" @click="resetView">🎯 重置视图</button>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts/core'; import { TreeChart } from 'echarts/charts'; import { TooltipComponent } from 'echarts/components'; import { CanvasRenderer } from 'echarts/renderers'
echarts.use([TreeChart, TooltipComponent, CanvasRenderer])
const props = defineProps({ height: { type: Number, default: 940 } }); const chartRef = ref(null); let chart = null
const mindMapData = { name: 'Java 语言全栈', symbolSize: 30, itemStyle: { color: '#1f2937' }, children: [
  { name: '📐 基础语法', itemStyle: { color: '#dc2626' }, children: [
    { name: 'OOP / 类与对象', link: '/01-basics/oop' }, { name: '数据类型 / 包装类', link: '/01-basics/datatypes' }, { name: '异常处理', link: '/01-basics/exceptions' }, { name: '泛型 / 注解 / 反射', link: '/01-basics/generics' }, { name: 'JDK 17-21 新特性', link: '/01-basics/new-features' }
  ]},
  { name: '📚 集合框架', itemStyle: { color: '#2563eb' }, children: [
    { name: 'List / ArrayList / LinkedList', link: '/02-collections/list' }, { name: 'Map / HashMap 原理', link: '/02-collections/map' }, { name: 'Set / TreeSet', link: '/02-collections/set' }, { name: 'Stream API', link: '/02-collections/stream' }, { name: '并发集合', link: '/02-collections/concurrent' }
  ]},
  { name: '🧵 并发编程', itemStyle: { color: '#9333ea' }, children: [
    { name: '线程 / 线程池', link: '/03-concurrency/thread-pool' }, { name: '锁 / synchronized / AQS', link: '/03-concurrency/locks' }, { name: 'JUC 工具', link: '/03-concurrency/juc' }, { name: 'CompletableFuture', link: '/03-concurrency/future' }, { name: '虚拟线程 (Loom)', link: '/03-concurrency/virtual-threads' }
  ]},
  { name: '⚙️ JVM 内存模型', itemStyle: { color: '#ea580c' }, children: [
    { name: 'JVM 运行时数据区', link: '/04-jvm/runtime' }, { name: '类加载机制', link: '/04-jvm/classloading' }, { name: '字节码 / 指令', link: '/04-jvm/bytecode' }, { name: '对象创建 / OOM 排查', link: '/04-jvm/oom' }
  ]},
  { name: '🗑️ GC 垃圾回收', itemStyle: { color: '#16a34a' }, children: [
    { name: 'GC 算法 (标记/复制/整理)', link: '/05-gc/algorithms' }, { name: 'G1 / ZGC / Shenandoah', link: '/05-gc/collectors' }, { name: 'GC 日志 / 调优', link: '/05-gc/tuning' }
  ]},
  { name: '🌱 Spring 核心', itemStyle: { color: '#06b6d4' }, children: [
    { name: 'IoC / DI / AOP', link: '/06-spring/ioc-aop' }, { name: 'Spring Boot 自动配置', link: '/06-spring/boot' }, { name: 'Spring MVC / WebFlux', link: '/06-spring/mvc' }, { name: '事务管理 / 声明式事务', link: '/06-spring/transaction' }
  ]},
  { name: '☁️ Spring Cloud', itemStyle: { color: '#0f766e' }, children: [
    { name: 'Nacos 注册/配置中心', link: '/07-spring-cloud/nacos' }, { name: 'Gateway / Sentinel', link: '/07-spring-cloud/gateway' }, { name: 'Seata 分布式事务', link: '/07-spring-cloud/seata' }
  ]},
  { name: '🗄️ DB / ORM', itemStyle: { color: '#f59e0b' }, children: [
    { name: 'JDBC / 连接池 (HikariCP)', link: '/08-database/jdbc' }, { name: 'MyBatis / MyBatis-Plus', link: '/08-database/mybatis' }, { name: 'JPA / Hibernate', link: '/08-database/jpa' }
  ]},
  { name: '📡 IO / NIO', itemStyle: { color: '#ec4899' }, children: [
    { name: 'BIO / NIO / AIO', link: '/09-io/nio' }, { name: 'Netty 框架', link: '/09-io/netty' }, { name: '序列化 / JSON / ProtoBuf', link: '/09-io/serialize' }
  ]},
  { name: '⚡ 性能调优', itemStyle: { color: '#ef4444' }, children: [
    { name: 'JVM 调优 (Xms/Xmx/GC)', link: '/10-performance/jvm-tuning' }, { name: 'Arthas 诊断', link: '/10-performance/arthas' }, { name: 'jstack / jmap / jstat', link: '/10-performance/jvm-tools' }
  ]},
  { name: '🏛️ 设计模式', itemStyle: { color: '#8b5cf6' }, children: [
    { name: '单例 / 工厂 / 建造者', link: '/11-design/creational' }, { name: '代理 / 装饰器 / 观察者', link: '/11-design/structural' }, { name: '策略 / 模板 / 责任链', link: '/11-design/behavioral' }
  ]},
  { name: '🛠️ 工具 / 构建', itemStyle: { color: '#84cc16' }, children: [
    { name: 'Maven / Gradle', link: '/12-tools/build' }, { name: 'Lombok / MapStruct', link: '/12-tools/lombok' }, { name: '常用命令速查', link: '/12-tools/commands' }
  ]},
  { name: '🧪 测试', itemStyle: { color: '#14b8a6' }, children: [
    { name: 'JUnit5', link: '/13-testing/junit5' }, { name: 'Mockito', link: '/13-testing/mockito' }, { name: 'Spring Boot Test', link: '/13-testing/spring-test' }
  ]},
  { name: '🎯 面试 / 进阶', itemStyle: { color: '#a855f7' }, children: [
    { name: '高频面试题', link: '/14-interview/questions' }, { name: '手写代码', link: '/14-interview/coding' }, { name: '项目案例 / 学习路径', link: '/14-interview/path' }
  ]}
] }

function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  chart.setOption({ tooltip: { trigger: 'item', triggerOn: 'mousemove', formatter: (p) => p.data?.link ? `<b>${p.name}</b><br/>点击跳转` : p.name },
    series: [{ type: 'tree', data: [mindMapData], top: '5%', left: '8%', bottom: '5%', right: '20%', symbolSize: 14, orient: 'LR', expandAndCollapse: true, initialTreeDepth: 2,
      label: { position: 'left', verticalAlign: 'middle', align: 'right', fontSize: 13, color: 'var(--vp-c-text-1, #333)' },
      leaves: { label: { position: 'right', verticalAlign: 'middle', align: 'left' } }, emphasis: { focus: 'descendant' }, animationDuration: 550, animationDurationUpdate: 750, lineStyle: { color: '#aaa', width: 1, curveness: 0.05 } }] })
  chart.on('click', (params) => { if (params.data?.link) window.location.href = params.data.link })
}
function expandAll() { if (!chart) return; const traverse = (node, depth) => { if (depth > 0 && node.children) chart.dispatchAction({ type: 'treeExpandAndCollapse', data: node, seriesIndex: 0 }); if (node.children) node.children.forEach(c => traverse(c, depth + 1)) }; traverse(mindMapData, 0) }
function collapseAll() { const traverse = (node) => { if (node.children) { node.children.forEach(c => { chart.dispatchAction({ type: 'treeExpandAndCollapse', data: c, seriesIndex: 0 }); traverse(c) }) } }; traverse(mindMapData) }
function resetView() { if (chart) chart.dispatchAction({ type: 'restore' }) }
onMounted(() => { renderChart(); window.addEventListener('resize', () => chart?.resize()) })
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>