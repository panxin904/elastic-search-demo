---
title: GraphQL / Apollo
date: 2026-08-15  # date-auto-injected
---

# GraphQL / Apollo

## 🎯 GraphQL 是什么

Facebook 提出的**API 查询语言**：客户端按需请求数据，避免 REST 的 over-fetch / under-fetch。

```graphql
# Schema
type User {
  id: ID!
  name: String!
  posts: [Post!]!
}
type Post {
  id: ID!
  title: String!
  author: User!
}
type Query {
  user(id: ID!): User
}
```

```graphql
# Query
query {
  user(id: "1") {
    name
    posts { title }
  }
}
```

```json
// Response
{
  "data": {
    "user": {
      "name": "alice",
      "posts": [{ "title": "Hello" }]
    }
  }
}
```

## 📦 Apollo Client (React)

```bash
npm install @apollo/client graphql
```

```tsx
import { ApolloClient, InMemoryCache, ApolloProvider, gql, useQuery } from '@apollo/client'

const client = new ApolloClient({
  uri: 'https://api.example.com/graphql',
  cache: new InMemoryCache()
})

<ApolloProvider client={client}>
  <App />
</ApolloProvider>

const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) { name posts { title } }
  }
`

function User({ id }) {
  const { data, loading, error } = useQuery(GET_USER, { variables: { id } })
  if (loading) return 'Loading'
  return <div>{data.user.name}</div>
}
```

### Mutations

```tsx
const ADD_POST = gql`
  mutation AddPost($title: String!) {
    addPost(title: $title) { id title }
  }
`

function NewPost() {
  const [add] = useMutation(ADD_POST, {
    refetchQueries: ['GetPosts']
  })

  return <button onClick={() => add({ variables: { title: 'X' } })}>+</button>
}
```

## 🆚 主流客户端

| | Apollo | urql | Relay |
|--|--------|------|-------|
| 缓存策略 | Normalized | Document | Normalized |
| Bundle | ~35KB | ~12KB | ~25KB |
| SSR | ✅ | ✅ | ✅ |
| 类型 | 自动 codegen | 自动 codegen | babel plugin |
| 学习曲线 | 中 | 平 | 陡 |

## ⚖️ Pros / Cons

| ✅ | ❌ |
|----|----|
| 一次请求取所有数据 | 服务端增加复杂度 |
| 类型安全（Schema 即类型） | 缓存设计需谨慎 |
| 便于前端组合查询 | HTTP 上传文件麻烦（multipart-spec） |
| DevTools 强 | SQL-like N+1 风险 |

## 🔧 服务器端

- **Apollo Server**（Node.js）
- **GraphQL Yoga**（现代化）
- **Hasura**（自动从 PG 生成 GraphQL）
- **PostGraphile**（自动从 PG 生成）
- **strawberry**（Python）

```ts
// Apollo Server
const server = new ApolloServer({
  typeDefs,
  resolvers
})
```

## 🔗 下一步

- [tRPC](/09-data/trpc)
- [REST 规范 / OpenAPI](/09-data/rest)
- [React Query](/07-state/data-fetching)
