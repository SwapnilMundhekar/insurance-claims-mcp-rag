\# 🛡️ MCP-Based Insurance Claims RAG Agent



<p align="center">

&#x20; <img src="https://img.shields.io/badge/Status-Part%201%20Complete-blue" />

&#x20; <img src="https://img.shields.io/badge/LLM-Local%20Ollama-green" />

&#x20; <img src="https://img.shields.io/badge/RAG-Semantic%20Chunking-purple" />

&#x20; <img src="https://img.shields.io/badge/MCP-Tool%20Calling-orange" />

&#x20; <img src="https://img.shields.io/badge/Cloud%20Target-AWS%20Bedrock-yellow" />

</p>



<p align="center">

&#x20; <b>Enterprise-grade local-first AI agent for insurance claims, policy intelligence, semantic RAG, MCP tools, and governed tool-calling pipelines.</b>

</p>



\---



\## 🚀 Project Vision



This project builds a \*\*local-first enterprise AI agent\*\* that can reason over insurance policy and regulatory documents, retrieve relevant clauses, and execute governed tool calls through an MCP-based architecture.



The goal is not to build a simple chatbot.



The goal is to build a \*\*senior AI engineering system\*\* where:



\* The LLM does \*\*not\*\* directly execute actions.

\* The application orchestrator validates and governs tool calls.

\* MCP servers expose controlled tools.

\* Insurance policy documents are semantically chunked and retrieved.

\* Every answer can be traced back to source documents.

\* Local development can later migrate to AWS using Claude on Amazon Bedrock.



\---



\## 🎯 Core Use Case



Example user question:



> “For this motor insurance claim, check whether accidental damage is covered, identify relevant exclusions, check complaint handling obligations, and draft a customer response.”



The system should eventually:



1\. Retrieve relevant policy clauses.

2\. Compare claim facts against coverage and exclusions.

3\. Retrieve regulatory obligations from AFCA, ASIC, Code of Practice, and APRA documents.

4\. Generate a grounded response with citations.

5\. Use MCP tools for retrieval, claim checks, audit logging, and controlled workflow actions.



\---



\## 🧠 Why This Project Matters



Most AI demos stop at:



```text

User question → LLM answer

```



This project goes further:



```text

User question

&#x20;  ↓

LLM reasoning

&#x20;  ↓

Structured tool call

&#x20;  ↓

Orchestrator validation

&#x20;  ↓

MCP tool execution

&#x20;  ↓

Semantic RAG retrieval

&#x20;  ↓

Grounded answer with citations

&#x20;  ↓

Trace and audit log

```



The key principle:



> \*\*The model proposes. The orchestrator validates. The MCP server executes.\*\*



\---



\## 🏗️ High-Level Architecture



```mermaid

flowchart TD

&#x20;   A\[User Question] --> B\[Local Agent App]

&#x20;   B --> C\[LLM via Ollama]

&#x20;   C --> D{Tool Required?}



&#x20;   D -- No --> E\[Direct Grounded Response]

&#x20;   D -- Yes --> F\[Tool-Calling Orchestrator]



&#x20;   F --> G\[Validate Tool Name]

&#x20;   G --> H\[Validate Arguments]

&#x20;   H --> I\[Apply Safety and Policy Checks]



&#x20;   I --> J\[MCP Client]

&#x20;   J --> K\[MCP Policy Knowledge Server]



&#x20;   K --> L\[Vector Store]

&#x20;   L --> M\[Semantic Chunks]

&#x20;   M --> N\[Insurance PDF Documents]



&#x20;   K --> O\[Tool Result]

&#x20;   O --> C

&#x20;   C --> P\[Final Answer with Citations]



&#x20;   F --> Q\[Trace Logs]

&#x20;   F --> R\[Audit Events]

```



\---



\## 📚 Knowledge Base Documents



The local knowledge base is built from insurance and regulatory PDF documents stored outside the Git repository.



Current local PDF folder:



```text

C:\\Users\\SSS\\Desktop\\AI Project\\pdf policy documents

```



Planned document categories:



| Category            | Example Documents                               | Purpose                                    |

| ------------------- | ----------------------------------------------- | ------------------------------------------ |

| Policy PDS          | NRMA Car Insurance PDS, NRMA Home Insurance PDS | Coverage, exclusions, claim conditions     |

| Claims Guidance     | AFCA claims handling guidance                   | Fair claims handling and dispute reasoning |

| Regulatory Guidance | ASIC INFO 253, ASIC RG 271                      | Claims handling and complaint obligations  |

| Industry Conduct    | General Insurance Code of Practice              | Customer treatment and industry standards  |

| Enterprise Risk     | APRA CPS 230                                    | Operational risk, resilience, controls     |



PDF files are intentionally excluded from GitHub using `.gitignore`.



\---



\## 🧩 Planned Local Stack



| Layer               | Technology                                              |

| ------------------- | ------------------------------------------------------- |

| Language            | Python                                                  |

| Local LLM Runtime   | Ollama                                                  |

| Local LLM           | Qwen / Llama family model                               |

| PDF Extraction      | PyMuPDF                                                 |

| Chunking            | Section-aware semantic chunking                         |

| Embeddings          | SentenceTransformers or local embedding model           |

| Vector Store        | ChromaDB                                                |

| Tool Interface      | MCP                                                     |

| Orchestration       | Custom Python orchestrator                              |

| UI                  | Streamlit                                               |

| Cloud Target        | Claude on Amazon Bedrock                                |

| Future Vector Store | Amazon OpenSearch Serverless or Bedrock Knowledge Bases |



\---



\## 🔥 Current Build Status



| Part | Module                                    | Status     |

| ---: | ----------------------------------------- | ---------- |

|    1 | Project skeleton and local setup          | ✅ Complete |

|    2 | PDF ingestion                             | ⏳ Next     |

|    3 | Cleaning and metadata extraction          | ⏳ Planned  |

|    4 | Section-aware semantic chunking           | ⏳ Planned  |

|    5 | Embeddings and local vector DB            | ⏳ Planned  |

|    6 | Retrieval testing                         | ⏳ Planned  |

|    7 | Ollama LLM integration                    | ⏳ Planned  |

|    8 | MCP policy knowledge server               | ⏳ Planned  |

|    9 | Governed tool-calling orchestrator        | ⏳ Planned  |

|   10 | Streamlit app, tracing, and documentation | ⏳ Planned  |



\---



\## 🧱 Repository Structure



```text

insurance-claims-mcp-rag/

│

├── app/

│   └── .gitkeep

│

├── config/

│   └── .gitkeep

│

├── data/

│   ├── raw/

│   │   └── .gitkeep

│   ├── processed/

│   │   └── .gitkeep

│   └── chunks/

│       └── .gitkeep

│

├── docs/

│   └── .gitkeep

│

├── logs/

│   └── .gitkeep

│

├── scripts/

│   └── .gitkeep

│

├── src/

│   ├── ingestion/

│   │   └── .gitkeep

│   ├── chunking/

│   │   └── .gitkeep

│   ├── retrieval/

│   │   └── .gitkeep

│   ├── llm/

│   │   └── .gitkeep

│   ├── mcp\_server/

│   │   └── .gitkeep

│   └── orchestrator/

│       └── .gitkeep

│

├── tests/

│   └── .gitkeep

│

├── vector\_store/

│   └── .gitkeep

│

├── .env.example

├── .gitignore

├── README.md

└── requirements.txt

```



\---



\## 🧬 Semantic Chunking Strategy



This project will not use naive word-based chunking.



The planned chunking strategy is:



```mermaid

flowchart LR

&#x20;   A\[PDF Page Text] --> B\[Text Cleaning]

&#x20;   B --> C\[Heading and Section Detection]

&#x20;   C --> D\[Clause-Aware Splitting]

&#x20;   D --> E\[Sentence and Paragraph Grouping]

&#x20;   E --> F\[Semantic Similarity Breakpoints]

&#x20;   F --> G\[Token Limit Guardrail]

&#x20;   G --> H\[Chunk Metadata]

&#x20;   H --> I\[Vector Store]

```



Each chunk will preserve metadata such as:



```text

document\_name

document\_type

provider\_or\_regulator

product\_type

section\_title

page\_number

chunk\_id

source\_path

```



This allows the agent to answer with traceable citations instead of unsupported text.



\---



\## 🛠️ Tool-Calling Pipeline



The final system will use a governed tool-calling pipeline.



```mermaid

sequenceDiagram

&#x20;   participant User

&#x20;   participant LLM

&#x20;   participant Orchestrator

&#x20;   participant MCP

&#x20;   participant VectorDB



&#x20;   User->>LLM: Ask insurance claim question

&#x20;   LLM->>Orchestrator: Structured tool request

&#x20;   Orchestrator->>Orchestrator: Validate tool name and arguments

&#x20;   Orchestrator->>Orchestrator: Apply safety and policy checks

&#x20;   Orchestrator->>MCP: Execute approved tool

&#x20;   MCP->>VectorDB: Search relevant chunks

&#x20;   VectorDB->>MCP: Return matched clauses

&#x20;   MCP->>Orchestrator: Tool result

&#x20;   Orchestrator->>LLM: Observation

&#x20;   LLM->>User: Grounded answer with citations

```



Core rule:



```text

LLM = reasoning and instruction generation

Orchestrator = validation and execution control

MCP server = governed tool interface

Vector DB = semantic knowledge layer

```



\---



\## 🧪 Planned MCP Tools



| Tool                        | Purpose                                              | Risk Level |

| --------------------------- | ---------------------------------------------------- | ---------- |

| `search\_policy\_documents`   | Retrieve relevant policy and regulatory chunks       | Low        |

| `get\_policy\_clause`         | Fetch a specific clause or section                   | Low        |

| `compare\_policy\_coverage`   | Compare claim facts against retrieved policy clauses | Medium     |

| `get\_complaint\_obligations` | Retrieve complaint and dispute obligations           | Low        |

| `draft\_customer\_response`   | Draft a customer-facing message                      | Medium     |

| `log\_audit\_event`           | Record trace and workflow event                      | Low        |



Future tools that create external side effects, such as sending emails or updating claims, should require approval gates.



\---



\## 🖥️ Local Setup



\### 1. Clone the repository



```bash

git clone https://github.com/SwapnilMundhekar/insurance-claims-mcp-rag.git

cd insurance-claims-mcp-rag

```



\### 2. Create virtual environment



```bash

python -m venv .venv

```



\### 3. Activate virtual environment on Windows



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



\### 4. Install dependencies



```bash

pip install -r requirements.txt

```



\### 5. Create local `.env`



Copy:



```bash

.env.example

```



to:



```bash

.env

```



Then update:



```text

PDF\_SOURCE\_DIR=C:\\Users\\SSS\\Desktop\\AI Project\\pdf policy documents

```



\---



\## ⚙️ Environment Variables



Example:



```text

PROJECT\_NAME=insurance-claims-mcp-rag

PROJECT\_ROOT=YOUR\_PROJECT\_PATH

PDF\_SOURCE\_DIR=YOUR\_POLICY\_PDF\_FOLDER\_PATH



OLLAMA\_BASE\_URL=http://localhost:11434

OLLAMA\_MODEL=qwen2.5:7b-instruct



VECTOR\_DB\_DIR=.\\vector\_store\\chroma

CHUNK\_OUTPUT\_DIR=.\\data\\chunks

PROCESSED\_OUTPUT\_DIR=.\\data\\processed

```



\---



\## 🧭 Development Roadmap



\### ✅ Part 1 — Project Skeleton



Completed:



\* Created project folder

\* Created Python virtual environment

\* Added source folders

\* Added `.gitignore`

\* Added `.env.example`

\* Added dependency file

\* Initialized Git repository



\### ⏭️ Part 2 — PDF Ingestion



Next goal:



\* Load all PDFs from local source directory

\* Extract text page by page

\* Preserve document name and page number

\* Save extracted output as structured JSON



Expected output:



```text

data/processed/extracted\_pages.json

```



\### ⏭️ Part 3 — Cleaning and Metadata



Planned:



\* Remove PDF extraction noise

\* Normalize whitespace

\* Preserve headings

\* Add document metadata

\* Classify documents by type



\### ⏭️ Part 4 — Semantic Chunking



Planned:



\* Split by headings and clauses

\* Group related sentences

\* Apply semantic breakpoints

\* Add chunk overlap and token guardrails

\* Save chunk objects



\### ⏭️ Part 5 — Vector Store



Planned:



\* Generate embeddings

\* Store chunks in ChromaDB

\* Add metadata filters

\* Build local search utility



\### ⏭️ Part 6 — Retrieval Evaluation



Planned:



\* Test sample insurance questions

\* Inspect top-k retrieved chunks

\* Validate citations

\* Improve chunk quality



\### ⏭️ Part 7 — Local LLM Integration



Planned:



\* Connect to Ollama

\* Generate grounded answers

\* Prevent unsupported claims

\* Include source citations



\### ⏭️ Part 8 — MCP Server



Planned:



\* Expose retrieval as MCP tools

\* Add tool schemas

\* Return structured results



\### ⏭️ Part 9 — Tool-Calling Orchestrator



Planned:



\* Let LLM propose tool calls

\* Validate tool calls

\* Execute MCP tools

\* Return observations back to LLM



\### ⏭️ Part 10 — Final Local App



Planned:



\* Streamlit UI

\* Trace panel

\* Source citation panel

\* Demo questions

\* Documentation

\* AWS migration plan



\---



\## 🎬 Demo Preview



Demo GIF will be added after the Streamlit application is built.



Planned location:



```text

docs/assets/demo.gif

```



Placeholder:



```markdown

!\[Demo Preview](docs/assets/demo.gif)

```



\---



\## 🧠 Senior Engineering Concepts Covered



This project demonstrates:



\* Local-first AI development

\* Retrieval-Augmented Generation

\* Section-aware semantic chunking

\* Metadata-driven retrieval

\* Tool calling

\* MCP server design

\* Agent orchestration

\* Validation before execution

\* Human approval gates

\* Audit logging

\* Enterprise insurance workflow modeling

\* AWS migration planning

\* Claude on Amazon Bedrock deployment path



\---



\## ☁️ Future AWS Deployment Plan



Local development stack:



```text

Ollama

ChromaDB

Local MCP server

Local PDFs

Streamlit

```



Future AWS stack:



```text

Claude on Amazon Bedrock

Amazon OpenSearch Serverless or Bedrock Knowledge Bases

S3 document storage

AWS Lambda or ECS for MCP services

CloudWatch logs

IAM access control

API Gateway

Streamlit or React frontend

```



Migration view:



```mermaid

flowchart LR

&#x20;   A\[Local PDFs] --> B\[S3 Document Bucket]

&#x20;   C\[ChromaDB] --> D\[OpenSearch Serverless]

&#x20;   E\[Ollama Local LLM] --> F\[Claude on Bedrock]

&#x20;   G\[Local MCP Server] --> H\[AWS Hosted MCP Services]

&#x20;   I\[Local Logs] --> J\[CloudWatch]

```



\---



\## ⚠️ Current Limitations



This project is under active development.



Current limitations:



\* PDF ingestion is not implemented yet.

\* Semantic chunking is planned but not implemented yet.

\* Vector database is not built yet.

\* MCP server is not implemented yet.

\* Tool-calling orchestration is not implemented yet.

\* No production deployment exists yet.

\* No real customer, claim, or private insurance data is included.



The project currently contains the initial repository structure and setup files only.



\---



\## 📌 Design Principle



> Build the system as if it will eventually run in an enterprise environment, even while testing locally.



That means:



\* No hardcoded secrets.

\* No PDFs committed to GitHub.

\* Clear module boundaries.

\* Traceable outputs.

\* Structured metadata.

\* Tool validation before execution.

\* Local-first development before cloud deployment.



\---



\## 👤 Author



\*\*Swapnil Mundhekar\*\*



GitHub: \[SwapnilMundhekar](https://github.com/SwapnilMundhekar)



\---



\## 📄 License



This project is currently for personal learning, portfolio development, and interview preparation.



A formal license can be added later.



