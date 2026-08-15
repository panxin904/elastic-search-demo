---
title: Flyweight 享元模式
description: 共享细粒度对象 + 减少内存 / Integer 缓存 / 文本编辑器 / 游戏地图 / 字符串池
---

# Flyweight 享元模式

## 核心问题

应用中需要大量相似对象（百万级 / 千万级），如果每个对象都独立存储，内存消耗巨大。

**真实场景**：
- 文本编辑器：每篇文章 10 万字，每个字符如果独立对象 = 100 MB
- 游戏地图：1000x1000 格子，每个格子独立对象 = 100 万元数据
- Java Integer 缓存：-128~127 是高频整数，全部缓存
- Java String 常量池：所有 `"hello"` 字面量共享一个对象

## 核心思想

把对象的**内部状态**（不变的部分）共享，把**外部状态**（变化的部分）从对象中抽离，由客户端在使用时传入。

**两种状态**：
- **内部状态（intrinsic）**：存储在享元对象内部，不随环境变化，可以共享
- **外部状态（extrinsic）**：由客户端传入（参数 / 上下文），享元对象不持有

## Java Integer 缓存

```java
Integer a = 127;
Integer b = 127;
System.out.println(a == b);  // true（同一对象，缓存命中）

Integer c = 128;
Integer d = 128;
System.out.println(c == d);  // false（不同对象，缓存未命中）

// 装箱
Integer e = Integer.valueOf(127);  // 从缓存取
Integer f = Integer.valueOf(128);  // 新建对象

// IntegerCache 源码（JDK 8+）
private static class IntegerCache {
    static final int low = -128;
    static final int high;  // 默认 127，但可配置 -XX:AutoBoxCacheMax=1000
    static final Integer cache[];

    static {
        int h = 127;
        String integerCacheHighPropValue = sun.misc.VM.getSavedProperty("java.lang.Integer.IntegerCache.high");
        if (integerCacheHighPropValue != null) {
            try { h = Integer.parseInt(integerCacheHighPropValue); } catch (...) {}
        }
        high = h;
        cache = new Integer[(high - low) + 1];
        int j = low;
        for (int k = 0; k < cache.length; k++) cache[k] = new Integer(j++);
    }

    public static Integer valueOf(int i) {
        if (i >= IntegerCache.low && i <= IntegerCache.high)
            return IntegerCache.cache[i + (-IntegerCache.low)];
        return new Integer(i);
    }
}
```

**注意**：`==` 比较引用，不能用于 Integer 一般场景（应该用 `.equals()`）。但在 -128~127 范围内 `==` 恰好为 true，会引发隐蔽 bug。

## 实战：文本编辑器

```java
class CharacterFlyweight {
    private final char ch;  // 内部状态（共享）
    private final Font font;

    public CharacterFlyweight(char ch, Font font) {
        this.ch = ch;
        this.font = font;
    }

    // 外部状态（位置 / 颜色）作为参数传入
    public void render(int x, int y, Color color) {
        font.drawChar(ch, x, y, color);
    }
}

// 享元工厂
class FontFactory {
    private static final Map<String, CharacterFlyweight> cache = new HashMap<>();

    public static CharacterFlyweight get(char ch, Font font) {
        String key = ch + "_" + font.getName();
        return cache.computeIfAbsent(key, k -> new CharacterFlyweight(ch, font));
    }
}

// 文本编辑器
class Document {
    private List<CharacterPosition> characters = new ArrayList<>();

    public void append(char ch, Font font, int x, int y) {
        // 字符本身（内部状态）从享元工厂取
        CharacterFlyweight fly = FontFactory.get(ch, font);
        // 位置（外部状态）由 Document 保存
        characters.add(new CharacterPosition(fly, x, y));
    }

    public void render() {
        for (CharacterPosition p : characters) {
            p.flyweight.render(p.x, p.y, currentColor);
        }
    }
}
```

**内存计算**：26 个字母 × 4 种字体 = 104 个享元（不管 1000 篇文章 × 10 万字）。
如果不享元：1000 × 100000 = 1 亿个对象。

## 实战：游戏地图

```typescript
// 地形类型（不变）
class TerrainTile {
    constructor(
        public readonly type: 'grass' | 'water' | 'mountain' | 'forest',
        public readonly texture: string,
        public readonly movementCost: number,
    ) {}

    render(x: number, y: number) {
        console.log(`Drawing ${this.type} at (${x},${y}) with texture ${this.texture}`);
    }
}

// 享元工厂
class TileFactory {
    private static tiles = new Map<string, TerrainTile>();

    static getTile(type: TerrainTile['type']): TerrainTile {
        if (!TileFactory.tiles.has(type)) {
            switch (type) {
                case 'grass': TileFactory.tiles.set(type, new TerrainTile(type, 'grass.png', 1)); break;
                case 'water': TileFactory.tiles.set(type, new TerrainTile(type, 'water.png', 3)); break;
                case 'mountain': TileFactory.tiles.set(type, new TerrainTile(type, 'mountain.png', 5)); break;
                case 'forest': TileFactory.tiles.set(type, new TerrainTile(type, 'forest.png', 2)); break;
            }
        }
        return TileFactory.tiles.get(type)!;
    }
}

// 地图（1000x1000 = 100 万格）
class GameMap {
    private grid: TerrainTile[][] = [];

    load() {
        for (let x = 0; x < 1000; x++) {
            this.grid[x] = [];
            for (let y = 0; y < 1000; y++) {
                const type = this.computeTileType(x, y);
                this.grid[x][y] = TileFactory.getTile(type);  // 共享！
            }
        }
    }

    render() {
        for (let x = 0; x < 1000; x++) {
            for (let y = 0; y < 1000; y++) {
                this.grid[x][y].render(x, y);  // 位置是外部状态
            }
        }
    }
}
```

**内存**：100 万格只有 4 个 TerrainTile 对象（不是 100 万个）。

## 适用边界

✅ **使用场景**：
- 大量相似对象（百万级 / 千万级）
- 对象的大部分状态可以外部化
- 对象创建成本高（IO / DB）

❌ **避免场景**：
- 对象数量不大（JVM GC 已经很快）
- 对象状态难以外部化
- 业务需要每个对象独立可变（享元不可变）

🔄 **与缓存的区别**：
- **享元**：在设计阶段就规划共享
- **缓存**：运行时按需缓存（懒加载）

💡 **最佳实践**：
- 享元对象必须是**不可变**的（否则共享会破坏业务）
- 内部状态 vs 外部状态划分要清晰
- 用工厂管理享元（避免重复创建）
- 注意线程安全（共享对象可能是多线程读）
