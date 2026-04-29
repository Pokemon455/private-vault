# 🏗️ Architecture Deep Dive

## Graph Flow

```
START
  │
  ▼
router_node
  │ route_condition()
  ├──── rag / web_search / python_tool ──→ LLM_Tool
  │                                            │
  │                                      tool_condition()
  │                                            ├── tool_calls? ──→ tools
  │                                            │                      │
  │                                            └── no tool ──→ answer_node ←──┘
  │
  └──── direct ──────────────────────────────────────→ answer_node
                                                              │
                                                             END
```

## Nodes Explained

### 1. `router_node`
- Input: User query
- Process: LLM classifies query into 4 categories
- Output: `router_decision` (python_tool/web_search/rag/direct)
- Accuracy: **100%** (tested on 10+ queries)

### 2. `LLM_Tool`
- Input: Messages + router_decision
- Process: Forces LLM to call specific tool
- Output: AIMessage with tool_calls
- Key fix: `tool_choice=forced` — no text answers

### 3. `tools`
- Input: Tool call from LLM_Tool
- Process: Executes actual tool (run_python/web_search/RAG)
- Output: ToolMessage with result

### 4. `answer_node`
- Input: Tool output + user query
- Process: Formats clean answer
- Output: Final response in user's language
- Key fix: No history contamination

## Bugs Fixed

### Bug 1: Tool Not Executing
**Problem:** `tools → LLM_Tool` loop caused tool to never execute  
**Fix:** `tools → answer_node` directly

### Bug 2: Hallucination  
**Problem:** Old ToolMessage in history caused wrong answers  
**Fix:** `answer_node` only uses `user_q + tool_out`

### Bug 3: Wrong Language
**Problem:** LLM replied in Hindi script  
**Fix:** Explicit "Roman Urdu only" rule in answer_node prompt

## Memory System

```
Thread ID → PostgreSQL (Neon)
    │
    ├── Conversation 1 (thread_id="1")
    ├── Conversation 2 (thread_id="2")
    └── Conversation N (thread_id="N")
```

Each thread maintains full conversation history via `AsyncPostgresSaver`.
