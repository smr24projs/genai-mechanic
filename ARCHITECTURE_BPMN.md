# GenAI Mechanic - BPMN Process Architecture
## Industry-Standard Agentic Workflow for Tata Technologies

---

## BPMN Symbol Legend

| Symbol | Name | Meaning |
|--------|------|---------|
| **●** | Terminator | Process Start/End Point |
| **▶** | Task | Process Execution Step |
| **◇** | Gateway | Decision Point / Conditional Branch |
| **⬢** | Service Task | External Tool / API Invocation |
| **▬▶** | Sequence Flow | Control/Data Flow Between Steps |
| **[M]** | Message Flow | Data Exchange Between Services |

---

## Complete Process Flow (BPMN Notation)

```
┌─ DIAGNOSTIC WORKFLOW ─────────────────────────────────────────────┐
│                                                                     │
│  ●[START]                                                          │
│    │                                                               │
│    ▬▶ User Input Reception                                        │
│    │                                                               │
│  ▶ Input Validation & Parsing                                     │
│    │                                                               │
│    ◇ Input Valid?                                                 │
│   /│\                                                              │
│  / │ \                                                             │
│ Y  N  (Clarifying Questions)                                      │
│ │  │                                                               │
│ │  └──▬▶ Request More Info ──────┐                               │
│ │                                 │                                │
│ ▶ Diagnostic Reasoning Phase       │                               │
│ │ (LLM Reasoning)                  │                               │
│ │                                  │                                │
│ ◇ Tools Required?                  │                               │
│/│\                                 │                               │
│ │ Yes (Tool Orchestration):        │                               │
│ │                                  │                               │
│ ├──▶ ⬢[ML CLASSIFIER]              │                               │
│ │    └─[M] Confidence Scores       │                               │
│ │                                  │                               │
│ ├──▶ ⬢[RAG DATABASE]               │                               │
│ │    └─[M] Knowledge Base Results  │                               │
│ │                                  │                               │
│ └──▶ ⬢[WEB SEARCH]                 │                               │
│      └─[M] External References     │                               │
│                                    │                               │
│ ▶ Service Result Aggregation      │                               │
│ │ (Tool Logger Node)               │                               │
│ │                                  │                               │
│ ◇ More Tools Needed?               │                               │
│  \                                 │                               │
│   └─ Yes? ───────────────▶[Re-evaluate with Reasoner]            │
│                                    │                               │
│       No? ▬▶                        │                               │
│            │                        │                               │
│  ▶ Response Synthesis              │                               │
│    - Combine Evidence              │                               │
│    - Calculate Confidence Scores   │                               │
│    - Format Action Plans           │                               │
│    - Add Safety Warnings           │                               │
│    │                               │                               │
│    ▬▶────────────────────────────┘                               │
│    │                                                               │
│  ▶ Output Formatting (JSON Serialization)                         │
│    │                                                               │
│    ▬▶ Response Delivery                                           │
│    │                                                               │
│  ●[END] - Session Complete                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Component Architecture

### 1. Input Processing (▶ Task)
```
User Input
    ▼
┌─────────────────────────────┐
│  Input Validation & Parsing │
│  - DTC Code Validation      │
│  - Sensor Value Validation  │
│  - Vehicle Model Validation │
└─────────────────────────────┘
    ▼
  ◇ Valid?
 /   \
Yes   No
 │     └─▶ [Clarifying Questions Response]
 ▼
Next Phase
```

### 2. Reasoning Phase (▶ + ◇ + ⬢)
```
┌────────────────────────────────────────┐
│    Diagnostic Reasoner (LLM)           │
│  - Command: invoke ChatGoogleGenerativeAI
│  - Temperature: 0.2 (deterministic)    │
│  - Context: Diagnostic Templates      │
└────────────────────────────────────────┘
                  ▼
            ◇ Decision Gateway
           /          |          \
      Tools?      No Tools    Clarify?
         │           │            │
         ▼           ▼            ▼
      Service    Final      Ask User
      Tasks      Answer     More Info
```

### 3. Service Orchestration (⬢ Service Tasks)

#### 3a. ML Classifier Service (⬢)
```
Input:  JSON sensor parameters
        {CAR_MODEL, ENGINE_RPM, ENGINE_LOAD, ...}

⬢ predict_root_cause
  - Service: scikit-learn classifier
  - Output: ml_score_hint (0-100)
         confidence predictions
         root cause probabilities

Output: Evidence + Score
```

#### 3b. RAG Database Service (⬢)
```
Input:  Diagnostic context
        DTC codes + symptoms

⬢ vehicle_diagnostic_db  
  - Service: Vector DB (LangChain RAG)
  - Output: RAG_SCORE_HINT (0-100)
         relevant service manual excerpts
         historical diagnostic patterns

Output: Knowledge Base Evidence + Score
```

#### 3c. Web Search Service (⬢)
```
Input:  Vehicle model + DTC + symptoms

⬢ vehicle_web_search
  - Service: Web Search API
  - Output: web_score (0-100)
         external references
         community solutions

Output: External Evidence + Score
```

### 4. Result Aggregation & Flow Control

```
┌─ Service Results Collected ─┐
│  ├─ ML Score: [0-100]       │
│  ├─ RAG Score: [0-100]      │
│  └─ Web Score: [0-100]      │
└─────────────────────────────┘
           ▼
     ◇ Gateway Decision
         /    \
      Yes     No
      More   All Info
     Tools?  Gathered
      │         │
      ▼         ▼
   Loop      Synthesize
   Back      Response

confidence_score = MAX(ml_score, rag_score, web_score)
```

### 5. Output Generation (▶)

```
Synthesis Phase:
  
  ▶ Combine Evidence
    - ML findings
    - RAG knowledge
    - Web references
    
  ▶ Calculate Scores
    - Confidence: max(ml, rag, web)
    - Weighted ranking
    
  ▶ Format Response
    - Generate diagnosis text
    - Create action plans (if repair steps needed)
    - Add safety warnings
    - Return JSON payload

Output Format (DiagnosticResponse):
{
  "needs_more_info": boolean,
  "diagnosis": string,
  "confidence_level": "High|Medium|Low",
  "confidence_score": 0-100,
  "ml_score": 0-100,
  "rag_score": 0-100,
  "web_score": 0-100,
  "action_plan": [...array of steps],
  "safety_warning": string
}
```

---

## Data Flow Diagram (BPMN [M] notation)

```
┌────────────┐
│  USER INPUT│ 
└────────────┘
     │
     [M] Input Data
     │
     ▼
┌──────────────────────┐
│  REASONER NODE       │──────────┐
│  (Diagnostic Reasoner)         │
└──────────────────────┘          │
     │                           │
     │ (Tool Calls?→ YES)        │
     │                           │
     ├─────────────────────┐     │
     │                     │     │
     ▼                     ▼     ▼
  ⬢ ML         ⬢ RAG       ⬢ WEB
  CLASSIFIER   DATABASE    SEARCH
     │             │         │
     [M]           [M]       [M]
   Scores        Results   External
     │             │         │
     └─────────┬───┴────┬────┘
               │        │
               ▼        ▼
         ┌──────────────────────┐
         │  TOOL LOGGER NODE    │
         │  (Aggregation)       │
         └──────────────────────┘
                  │
                  [M] Aggregated Evidence
                  │
                  ▼
         ┌──────────────────────┐
         │  REASONER (Round 2)  │
         │  (Synthesis)         │
         └──────────────────────┘
                  │
                  ▼
         ┌──────────────────────┐
         │  OUTPUT FORMATTER    │
         │  (JSON Serialization)│
         └──────────────────────┘
                  │
                  ▼
         ┌──────────────────────┐
         │  DIAGNOSTIC RESPONSE │
         │  (JSON Object)       │
         └──────────────────────┘
```

---

## Process States (LangGraph Nodes)

| Node | Type | Purpose | BPMN Equivalent |
|------|------|---------|-----------------|
| **START** | Gateway | Process initialization | ● |
| **Reasoner** | LLM Task | Invoke LLM reasoning engine | ▶ |
| **Tools** | ToolNode | Execute service tasks in parallel | ⬢ (batched) |
| **Logger** | Processing | Aggregate and route tool results | ▶ |
| **END** | Gateway | Process termination | ● |

---

## Edge Connections (Control Flow)

```
START ──▬▶ REASONER
            │
            ◇ Decision: Tools needed?
           ╱ ╲
         Yes   No
         │     └──▬▶ END
         │
         ▼
     TOOLS (Parallel Execution)
         │
         ├──▬▶ ML_CLASSIFIER
         ├──▬▶ RAG_DATABASE  
         └──▬▶ WEB_SEARCH
             │
             ▼
       LOGGER (Aggregation)
             │
             ▬▶ REASONER (Synthesis Loop)
                  │
                  ◇ More tools?
                 ╱  ╲
               Yes   No
               │     └──▬▶ END
               │
               └─────────┘ (Re-loop)
```

---

## Execution Sequence (Swimlane)

```
┌────────────────────────────────────────────────────────────────┐
│  GenAI Mechanic: Diagnostic Workflow Execution Sequence        │
└────────────────────────────────────────────────────────────────┘

Time    │  User          Reasoner       Tools          Output
        │  (Input)       (LLM)          (Services)     (Response)
────────┼────────────────────────────────────────────────────────
  T=0   │  
        │  ●[Input]
        │   ├──[M] Send Diagnostic Query
        │   │        ▬▶ ▶ [Validate & Parse]
        │   │              │
  T=1   │   │              ◇ Valid?──Yes──▼
        │   │              │          ├──[M] Confirmed
        │   │              No         │
        │   │              │     ▶ [Identify Missing Info]
  T=2   │   │              └─────────▬▶ [Query User]
        │   │
  T=3   │   │         ▶ [Invoke Reasoner (1st Pass)]
        │   │          - Load diagnostic template
        │   │          - Analyze input context
        │   │              │
  T=4   │   │              ◇ Tools Required?
        │   │             /        \
        │   │          Yes         No
        │   │           │           └──▼
        │   │           ▼         ▶ [Final Synthesis]
        │   │         ⬢ SERVICE INVOCATION (PARALLEL)
        │   │           ├──────────▬▶ ⬢ ML       @T=5-10
        │   │           ├──────────▬▶ ⬢ RAG      @T=5-12  
        │   │           └──────────▬▶ ⬢ WEB      @T=5-8
        │   │
  T=13  │   │         ▶ [Aggregate Results]
        │   │         └──[M]  Results Collected
        │   │             │
  T=14  │   │         ▶ [Synthesize Evidence]
        │   │          - Combine scores
        │   │          - Rank solutions
        │   │          - Create action plan
        │   │              │
  T=15  │   │              ▼
        │   └───────────────────[M]────────────────▶ ● JSON Response
        │                                          │
  T=16  │              ◇──────────────────────────────┘
        │             Loop? (if more tools needed)     [END Session]
        │                  │                            │
        │                  └─▬▶ [Re-evaluate] ────────┘
        │
────────┴────────────────────────────────────────────────────────

Legend:  ● = Start/End
         ▶ = Task Execution
         ◇ = Decision
         ⬢ = Service Call
         [M] = Message/Data Flow
         ▬▶ = Control Flow
```

---

## Implementation Notes

### Key BPMN Principles Implemented

1. **Clear Process Boundaries**: Start (●) → Steps (▶) → End (●)
2. **Explicit Decision Points**: All conditionals use gateway (◇) notation
3. **Service Abstraction**: Tools represented as service tasks (⬢)
4. **Data Flow Clarity**: Message flows ([M]) show data movement between components
5. **Control Flow**: Sequence flows (▬▶) show execution order
6. **Error Handling**: Implicit in decision gateways (valid input? → yes/no paths)

### Terminal Output Format (BPMNLogger)

The refactored code now outputs process flow using BPMN symbols:

```
● [DIAGNOSTIC REASONING]
─ ▶ TASK: LLM Inference | Initializing reasoning phase
─ ◇ DECISION: Tool calls required → Routing to Service Invocation
─ ⬢ SERVICE: predict_root_cause | Args: {...}
─ ⬢ SERVICE: vehicle_diagnostic_db | Args: {...}
─ ⬢ SERVICE: vehicle_web_search | Args: {...}
─ [M] ML_CLASSIFIER ▬▶ REASONER [Confidence Scores]
─ [M] RAG_DATABASE ▬▶ REASONER [Knowledge Base Results]
─ [M] WEB_SEARCH ▬▶ REASONER [External References]
─ ◇ DECISION: Analysis complete → Synthesizing final response
─ ▶ TASK: Output Generation | Formatting final diagnostic response
─ ● COMPLETE: Session concluded successfully
```

---

## Industry Compliance

✅ **BPMN 2.0 Standard**: Follows OMG Business Process Model and Notation  
✅ **Enterprise-Grade Visualization**: Professional symbols, no casual emoji  
✅ **TTL Standards**: Aligns with enterprise diagnostic workflow practices  
✅ **Traceability**: Every decision and service invocation is explicit  
✅ **Maintainability**: Clear process documentation for future iterations  

---

**Document Version**: 1.0  
**Last Updated**: April 2026  
**Architecture**: LangGraph + BPMN 2.0  
**Target**: GenAI Mechanic v2.0 - TTL Technologies
