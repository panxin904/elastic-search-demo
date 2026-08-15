"""System and user prompts for the grounded RAG generator.

The system prompt is the single most important piece of the whole
project: it implements the **Source-Grounding isolation** behaviour
described in `notebooklm_architecture.md` §2.1. The LLM is forbidden
from using its pretrained knowledge; every claim must be backed by
a retrieved chunk and tagged with a `[source_N]` marker.
"""
from __future__ import annotations

from notebooklm.generation.llm_provider import Message

NO_CONTEXT_RESPONSE = "源文件中未提及此内容。"


_SYSTEM_PROMPT = """\
你是 NotebookLM 助手。你必须严格按照以下规则回答用户问题。

## 规则
1. 你只能使用 <context> 标签内的源文件内容回答问题。严禁使用预训练知识、严禁编造。
2. 在每个事实主张后插入引用标记，格式为 [source_N]，N 是 <context> 中对应块的编号（从 1 开始）。
3. 如果 <context> 中的内容不足以回答问题，必须回答：「{no_context}」
4. 回答应保持简洁、严谨；不要给出与问题无关的内容。

## 输出格式
- 每个事实主张必须有 [source_N] 引用。
- 引用标记紧跟在事实之后，例如：「LangGraph 是一个编排框架 [source_1]。」
- 不要把多个引用堆在一起；每个事实单独标号。
"""


_USER_TEMPLATE = """\
<context>
{contexts}
</context>

用户问题：{query}

请基于 <context> 回答。"""


def build_grounded_prompt(
    query: str,
    contexts: list[str],
    no_context_response: str = NO_CONTEXT_RESPONSE,
) -> list[Message]:
    """Assemble the system + user messages for the grounded RAG call.

    If ``contexts`` is empty, the user message is replaced with a hard
    instruction to respond with the no-context fallback string. This
    mirrors the validation loop: when retrieval returns nothing, the
    LLM should explicitly say "not mentioned" rather than hallucinate.
    """
    system = _SYSTEM_PROMPT.format(no_context=no_context_response)
    if not contexts:
        user = (
            "<context>\n(无相关内容)\n</context>\n\n"
            f"用户问题：{query}\n\n请基于 <context> 回答。"
        )
    else:
        joined = "\n\n".join(f"[source_{i + 1}] {c}" for i, c in enumerate(contexts))
        user = _USER_TEMPLATE.format(contexts=joined, query=query)
    return [
        Message(role="system", content=system),
        Message(role="user", content=user),
    ]
