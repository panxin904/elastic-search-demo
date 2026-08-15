// frontend-html graph data
// 节点分类：foundation / language / framework / meta / build / style / state / routing / data / testing / node / perf / interview / tools

export const graphData = {
  nodes: [
    // 基础
    { name: 'HTML 语义化', category: 'foundation', link: '/01-foundation/html', value: 5 },
    { name: 'CSS 基础', category: 'foundation', link: '/01-foundation/css', value: 5 },
    { name: '浏览器渲染', category: 'foundation', link: '/01-foundation/browser', value: 6 },
    { name: 'Event Loop', category: 'foundation', link: '/01-foundation/event-loop', value: 6 },
    { name: 'Web 协议', category: 'foundation', link: '/01-foundation/protocol', value: 4 },

    // 语言
    { name: 'JavaScript', category: 'language', link: '/02-language/javascript', value: 8 },
    { name: 'TypeScript', category: 'language', link: '/02-language/typescript', value: 8 },
    { name: 'ESNext', category: 'language', link: '/02-language/esnext', value: 5 },
    { name: 'WebAssembly', category: 'language', link: '/02-language/wasm', value: 3 },

    // 框架
    { name: 'React', category: 'framework', link: '/03-framework/react', value: 9 },
    { name: 'Vue', category: 'framework', link: '/03-framework/vue', value: 8 },
    { name: 'Angular', category: 'framework', link: '/03-framework/angular', value: 5 },
    { name: 'Svelte', category: 'framework', link: '/03-framework/svelte', value: 5 },
    { name: '框架选型', category: 'framework', link: '/03-framework/overview', value: 5 },

    // 元框架
    { name: 'Next.js', category: 'meta', link: '/04-meta/nextjs', value: 8 },
    { name: 'Nuxt', category: 'meta', link: '/04-meta/nuxt', value: 6 },
    { name: 'Remix', category: 'meta', link: '/04-meta/remix', value: 5 },
    { name: 'SvelteKit', category: 'meta', link: '/04-meta/sveltekit', value: 5 },
    { name: 'Astro / Qwik', category: 'meta', link: '/04-meta/astro', value: 4 },

    // 构建
    { name: 'Vite', category: 'build', link: '/05-build/vite', value: 7 },
    { name: 'Webpack / Rspack', category: 'build', link: '/05-build/webpack', value: 7 },
    { name: 'esbuild', category: 'build', link: '/05-build/esbuild', value: 5 },
    { name: '包管理', category: 'build', link: '/05-build/package-manager', value: 5 },
    { name: 'Monorepo', category: 'build', link: '/05-build/monorepo', value: 5 },

    // 样式
    { name: '预处理器', category: 'style', link: '/06-style/preprocessor', value: 4 },
    { name: 'Tailwind', category: 'style', link: '/06-style/tailwind', value: 8 },
    { name: 'CSS-in-JS', category: 'style', link: '/06-style/css-in-js', value: 5 },
    { name: 'CSS Modules', category: 'style', link: '/06-style/css-modules', value: 4 },
    { name: '设计系统', category: 'style', link: '/06-style/design-system', value: 5 },

    // 状态
    { name: 'Redux', category: 'state', link: '/07-state/redux', value: 6 },
    { name: 'Zustand', category: 'state', link: '/07-state/zustand', value: 5 },
    { name: 'Pinia', category: 'state', link: '/07-state/pinia', value: 5 },
    { name: 'React Query', category: 'state', link: '/07-state/data-fetching', value: 6 },

    // 路由
    { name: 'React Router', category: 'routing', link: '/08-routing/react-router', value: 6 },
    { name: 'Vue Router', category: 'routing', link: '/08-routing/vue-router', value: 5 },
    { name: 'TanStack Router', category: 'routing', link: '/08-routing/tanstack-router', value: 4 },
    { name: 'File Routing', category: 'routing', link: '/08-routing/file-routing', value: 4 },

    // 数据层
    { name: 'GraphQL', category: 'data', link: '/09-data/graphql', value: 6 },
    { name: 'tRPC', category: 'data', link: '/09-data/trpc', value: 5 },
    { name: 'REST / OpenAPI', category: 'data', link: '/09-data/rest', value: 6 },
    { name: 'Realtime', category: 'data', link: '/09-data/realtime', value: 4 },

    // 测试
    { name: 'Jest/Vitest', category: 'testing', link: '/10-testing/unit', value: 6 },
    { name: 'RTL', category: 'testing', link: '/10-testing/rtl', value: 5 },
    { name: 'E2E', category: 'testing', link: '/10-testing/e2e', value: 5 },
    { name: 'Storybook', category: 'testing', link: '/10-testing/storybook', value: 4 },

    // Node
    { name: 'Node 运行时', category: 'node', link: '/11-node/runtime', value: 6 },
    { name: 'Express', category: 'node', link: '/11-node/express', value: 6 },
    { name: 'NestJS', category: 'node', link: '/11-node/nestjs', value: 7 },
    { name: 'Fastify / Hono', category: 'node', link: '/11-node/fastify', value: 5 },
    { name: 'Serverless', category: 'node', link: '/11-node/serverless', value: 5 },

    // 性能
    { name: 'CWV', category: 'perf', link: '/12-perf/cwv', value: 5 },
    { name: '加载性能', category: 'perf', link: '/12-perf/loading', value: 6 },
    { name: '运行时性能', category: 'perf', link: '/12-perf/runtime', value: 6 },
    { name: '可访问性', category: 'perf', link: '/12-perf/a11y', value: 4 },

    // 面试
    { name: '高频面试题', category: 'interview', link: '/13-interview/basic', value: 7 },
    { name: '手写代码', category: 'interview', link: '/13-interview/coding', value: 6 },
    { name: '系统设计', category: 'interview', link: '/13-interview/system', value: 6 },

    // 工程化
    { name: 'Lint/Format', category: 'tools', link: '/14-tools/lint', value: 4 },
    { name: 'CI/CD', category: 'tools', link: '/14-tools/cicd', value: 4 },
    { name: '监控', category: 'tools', link: '/14-tools/monitor', value: 4 },
    { name: '微前端', category: 'tools', link: '/14-tools/micro-frontend', value: 5 }
  ],

  links: [
    // 基础 → 语言
    { source: 'HTML 语义化', target: 'JavaScript' },
    { source: 'CSS 基础', target: 'JavaScript' },
    { source: '浏览器渲染', target: 'Event Loop' },
    { source: 'Event Loop', target: 'JavaScript' },
    { source: 'JavaScript', target: 'TypeScript' },
    { source: 'TypeScript', target: 'ESNext' },
    { source: 'TypeScript', target: 'WebAssembly' },

    // 语言 → 框架
    { source: 'JavaScript', target: 'React' },
    { source: 'JavaScript', target: 'Vue' },
    { source: 'JavaScript', target: 'Angular' },
    { source: 'JavaScript', target: 'Svelte' },
    { source: 'TypeScript', target: '框架选型' },

    // 框架 → 元框架
    { source: 'React', target: 'Next.js' },
    { source: 'React', target: 'Remix' },
    { source: 'Vue', target: 'Nuxt' },
    { source: 'Svelte', target: 'SvelteKit' },
    { source: '框架选型', target: 'Astro / Qwik' },

    // 框架 → 构建
    { source: 'Next.js', target: 'Vite' },
    { source: 'Nuxt', target: 'Webpack / Rspack' },
    { source: '框架选型', target: 'Vite' },
    { source: '框架选型', target: 'Webpack / Rspack' },
    { source: 'Vite', target: 'esbuild' },
    { source: 'Webpack / Rspack', target: 'esbuild' },
    { source: '框架选型', target: '包管理' },
    { source: '包管理', target: 'Monorepo' },
    { source: 'Monorepo', target: '包管理' },

    // 框架 → 状态
    { source: 'React', target: 'Redux' },
    { source: 'React', target: 'Zustand' },
    { source: 'React', target: 'React Query' },
    { source: 'Vue', target: 'Pinia' },

    // 框架 → 路由
    { source: 'React', target: 'React Router' },
    { source: 'Vue', target: 'Vue Router' },
    { source: 'React Router', target: 'TanStack Router' },
    { source: 'Next.js', target: 'File Routing' },
    { source: 'Nuxt', target: 'File Routing' },
    { source: 'Remix', target: 'File Routing' },
    { source: 'Astro / Qwik', target: 'File Routing' },

    // 框架 → 数据层
    { source: 'React', target: 'GraphQL' },
    { source: 'React', target: 'tRPC' },
    { source: 'React', target: 'REST / OpenAPI' },
    { source: 'Vue', target: 'REST / OpenAPI' },

    // 框架 → 样式
    { source: 'CSS 基础', target: '预处理器' },
    { source: 'CSS 基础', target: 'Tailwind' },
    { source: 'CSS 基础', target: 'CSS-in-JS' },
    { source: 'CSS 基础', target: 'CSS Modules' },
    { source: 'Tailwind', target: '设计系统' },
    { source: 'CSS-in-JS', target: '设计系统' },

    // 框架 → 测试
    { source: 'React', target: 'Jest/Vitest' },
    { source: 'Vue', target: 'Jest/Vitest' },
    { source: 'React', target: 'RTL' },
    { source: 'Jest/Vitest', target: 'E2E' },
    { source: 'RTL', target: 'E2E' },
    { source: '设计系统', target: 'Storybook' },

    // 语言/基础 → Node
    { source: 'JavaScript', target: 'Node 运行时' },
    { source: 'Web 协议', target: 'Express' },
    { source: 'Node 运行时', target: 'Express' },
    { source: 'Node 运行时', target: 'NestJS' },
    { source: 'Node 运行时', target: 'Fastify / Hono' },
    { source: 'NestJS', target: 'Serverless' },
    { source: 'Fastify / Hono', target: 'Serverless' },

    // Node → 数据层
    { source: 'Express', target: 'GraphQL' },
    { source: 'NestJS', target: 'tRPC' },
    { source: 'Express', target: 'REST / OpenAPI' },
    { source: 'Realtime', target: 'Express' },

    // 框架 → 性能
    { source: 'Next.js', target: 'CWV' },
    { source: 'Nuxt', target: 'CWV' },
    { source: 'Vite', target: '加载性能' },
    { source: 'Webpack / Rspack', target: '加载性能' },
    { source: 'CSS 基础', target: '可访问性' },

    // 数据层 → 性能
    { source: 'React Query', target: '运行时性能' },
    { source: 'GraphQL', target: '运行时性能' },

    // 实时
    { source: 'REST / OpenAPI', target: 'Realtime' },

    // 状态 → 数据层
    { source: 'React Query', target: 'GraphQL' },
    { source: 'React Query', target: 'tRPC' },

    // 测试 → 工程化
    { source: 'E2E', target: 'CI/CD' },
    { source: 'Storybook', target: 'CI/CD' },

    // 工程化 → 框架
    { source: 'Lint/Format', target: 'React' },
    { source: 'Lint/Format', target: 'Vue' },
    { source: '监控', target: '运行时性能' },
    { source: '微前端', target: 'React' },
    { source: '微前端', target: 'Vue' },

    // 面试 → 全部 (概括关联)
    { source: 'JavaScript', target: '高频面试题' },
    { source: 'TypeScript', target: '高频面试题' },
    { source: 'React', target: '手写代码' },
    { source: 'Vue', target: '手写代码' },
    { source: 'Next.js', target: '系统设计' },
    { source: 'NestJS', target: '系统设计' },
    { source: 'React Query', target: '系统设计' },
    { source: 'Monorepo', target: '系统设计' }
  ]
}
