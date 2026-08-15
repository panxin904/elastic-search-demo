# LangGraph Source-Grounded RAG

LangGraph is a framework for building stateful, multi-actor applications
with large language models. It is built on top of LangChain and extends
the LangChain Expression Language with the ability to coordinate multiple
chains (or actors) across multiple steps of computation in a cyclic
manner.

## Architecture

LangGraph models an application as a directed graph. Nodes represent
computation steps and edges represent the flow of data between them. The
framework enforces a Source-Grounding discipline: every node only sees
the data passed to it through the shared state, and the state itself
must be derived from a known source — never from the model's prior
knowledge.

## Source-Grounded Retrieval

A typical LangGraph RAG pipeline looks like this:

1. The user asks a question.
2. The retriever pulls the top K chunks from a vector store using cosine
   similarity. The vector store contains only documents the user has
   ingested, so the LLM cannot hallucinate from public training data.
3. The reranker cross-encodes the candidates with the query and keeps
   the top N most relevant chunks.
4. The generator receives the query plus the N chunks as a single
   prompt and is explicitly instructed to answer only from those
   chunks, with citations of the form [source_N].

## Why Grounding Matters

Source-Grounding is critical for factual accuracy. When an LLM is
allowed to mix retrieved context with its own parametric knowledge,
the user can no longer trust which parts of the answer came from
where. LangGraph's design forces the developer to keep these two
streams separate: the model output must be either pure retrieval, or
explicitly labeled as a synthesis step.

## Common Patterns

- **Citation tokens**: every generated sentence carries a token like
  [source_1] that maps back to a specific chunk in the source
  document. The UI can then render a clickable card next to each
  sentence.
- **Validation loops**: after generation, a separate node checks that
  every citation token references a chunk that was actually retrieved.
  If any are missing, the graph loops back to the generator with a
  retry instruction.
- **Multi-hop retrieval**: when one retrieval pass is not enough, the
  graph can use the first answer to formulate a follow-up query and
  retrieve again, with the results accumulated in the shared state.
