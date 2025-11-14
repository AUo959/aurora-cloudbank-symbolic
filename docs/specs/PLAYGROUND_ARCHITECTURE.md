# Playground Architecture Specification

**Project:** Aurora CloudBank Symbolic Web Playground
**Version:** 1.0
**Date:** 2025-11-09
**Status:** Design

---

## 1. Overview

The Aurora Playground is a browser-based interactive development environment that allows developers to experiment with Aurora APIs without local setup. It features a code editor, execution sandbox, scenario gallery, and real-time output display.

### 1.1 Goals

- **Zero Setup:** No installation required, instant experimentation
- **Educational:** Interactive tutorials and examples
- **Shareable:** URLs encode code for easy sharing
- **Safe:** Sandboxed execution with resource limits
- **Fast:** Sub-3-second execution time

### 1.2 User Experience Flow

```
┌─────────────┐
│ Landing     │──> Choose Scenario from Gallery
│ Page        │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Code Editor │──> Edit Code ──> Click "Run"
│             │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Execution   │──> Show Progress
│ Sandbox     │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Output      │──> Display Results
│ Console     │
└─────────────┘
       │
       ▼
┌─────────────┐
│ Share/Fork  │──> Generate URL
│ Save        │
└─────────────┘
```

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Client (Browser)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Editor     │  │   Output     │  │   Gallery    │     │
│  │  (Monaco)    │  │  (Console)   │  │  (Examples)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  ▲                │               │
│         │                  │                │               │
│         ▼                  │                ▼               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           State Management (Zustand/Jotai)           │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬──────────────────────────────────┘
                         │ HTTPS/WebSocket
                         │
┌────────────────────────▼──────────────────────────────────┐
│              Playground Backend (FastAPI)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Execution   │  │   Session    │  │   Metrics    │    │
│  │  Controller  │  │   Manager    │  │   Tracker    │    │
│  └──────┬───────┘  └──────────────┘  └──────────────┘    │
│         │                                                  │
└─────────┼──────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────┐
│        Container Orchestrator (Docker/K8s)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Python      │  │   Node.js    │  │   Resource   │   │
│  │  Sandbox     │  │   Sandbox    │  │   Monitor    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└──────────────────────────────────────────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────┐
│              Aurora API (Backend Services)                │
│  • Quantum Simulation                                     │
│  • Memory Management                                      │
│  • Thread Bridge                                          │
│  • Decision Intelligence                                  │
└──────────────────────────────────────────────────────────┘
```

### 2.2 Component Breakdown

#### Frontend (React + TypeScript)
- **Code Editor:** Monaco Editor (VSCode in browser)
- **UI Framework:** React 18+ with TypeScript
- **Styling:** Tailwind CSS + shadcn/ui
- **State:** Zustand or Jotai (lightweight)
- **Build:** Vite (fast builds, HMR)
- **Deployment:** Vercel or Netlify

#### Backend (FastAPI + Python)
- **Framework:** FastAPI 0.118+
- **Session Storage:** Redis (15-minute TTL)
- **Execution Queue:** Celery or RQ
- **Container Runtime:** Docker SDK
- **Monitoring:** Prometheus metrics
- **Rate Limiting:** 100 executions/hour per IP

#### Sandbox (Docker Containers)
- **Base Images:** python:3.11-slim, node:20-slim
- **Isolation:** No network access, restricted filesystem
- **Limits:** 512MB RAM, 30s timeout, 1 CPU core
- **Security:** AppArmor/SELinux, read-only root filesystem

---

## 3. Frontend Design

### 3.1 UI Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  Aurora Playground            [Save] [Share] [Fork] [Run ▶]      │
├───────────────────┬──────────────────────────────────────────────┤
│  Examples         │  1  from aurora_sdk import AuroraClient      │
│  ├─ Quantum       │  2                                           │
│  │  ├─ Supply    │  3  client = AuroraClient()                  │
│  │  ├─ Energy    │  4                                           │
│  │  └─ Risk      │  5  # Run quantum scenario                   │
│  ├─ Decision      │  6  result = await client.quantum.run...    │
│  │  ├─ Oracle    │  7                                           │
│  │  └─ Monte C.  │  8  print(result)                            │
│  └─ Memory        │  9                                           │
│                   │ 10                                           │
│  Settings         │                                              │
│  • Language: Python                                              │
│  • Theme: Dark    ├──────────────────────────────────────────────┤
│  • Font: 14px     │  Console Output:                             │
│                   │  > Running scenario...                       │
│  Share            │  > Quantum circuit compiled                  │
│  [Copy Link]      │  > Simulation complete                       │
│  [Embed Code]     │  {                                           │
│  [Export .py]     │    "optimal_state": [1, 0, 1, 0, 1],        │
│                   │    "cost_reduction": 23.4,                   │
│                   │    "execution_time": 1.24                    │
│                   │  }                                           │
└───────────────────┴──────────────────────────────────────────────┘
```

### 3.2 Component Structure

```
src/
├── App.tsx                      # Main app component
├── components/
│   ├── Editor/
│   │   ├── CodeEditor.tsx       # Monaco editor wrapper
│   │   ├── EditorToolbar.tsx    # Run, Save, Share buttons
│   │   └── LanguageSelector.tsx # Python/JS selector
│   ├── Output/
│   │   ├── Console.tsx          # Output console
│   │   ├── OutputPanel.tsx      # Results display
│   │   └── ErrorDisplay.tsx     # Error formatting
│   ├── Sidebar/
│   │   ├── ExampleGallery.tsx   # Scenario examples
│   │   ├── Settings.tsx         # Editor settings
│   │   └── SharePanel.tsx       # Share options
│   └── Layout/
│       ├── Header.tsx           # Top bar
│       ├── Sidebar.tsx          # Left sidebar
│       └── SplitPane.tsx        # Resizable panes
├── hooks/
│   ├── useCodeExecution.ts      # Execute code
│   ├── useSession.ts            # Session management
│   └── useExamples.ts           # Load examples
├── services/
│   ├── api.ts                   # Backend API client
│   ├── websocket.ts             # WebSocket client
│   └── storage.ts               # LocalStorage wrapper
├── store/
│   └── playgroundStore.ts       # Zustand store
└── types/
    └── playground.ts            # TypeScript types
```

### 3.3 State Management (Zustand)

```typescript
interface PlaygroundState {
  // Code
  code: string;
  language: 'python' | 'javascript';

  // Execution
  isExecuting: boolean;
  output: string[];
  error: string | null;

  // Session
  sessionId: string | null;
  shareUrl: string | null;

  // UI
  theme: 'light' | 'dark';
  fontSize: number;

  // Actions
  setCode: (code: string) => void;
  executeCode: () => Promise<void>;
  shareSession: () => Promise<string>;
  loadExample: (example: string) => void;
}

const usePlaygroundStore = create<PlaygroundState>((set, get) => ({
  code: '',
  language: 'python',
  isExecuting: false,
  output: [],
  error: null,
  sessionId: null,
  shareUrl: null,
  theme: 'dark',
  fontSize: 14,

  setCode: (code) => set({ code }),

  executeCode: async () => {
    set({ isExecuting: true, output: [], error: null });
    try {
      const result = await executeCode(get().code, get().language);
      set({ output: result.output, isExecuting: false });
    } catch (error) {
      set({ error: error.message, isExecuting: false });
    }
  },

  shareSession: async () => {
    const url = await createShareUrl(get().code, get().language);
    set({ shareUrl: url });
    return url;
  },

  loadExample: (example) => {
    const code = EXAMPLES[example];
    set({ code });
  }
}));
```

### 3.4 Example Gallery Data

```typescript
const EXAMPLES = {
  'quantum/supply_chain': {
    title: 'Supply Chain Optimization',
    description: 'Optimize supply chain with quantum algorithms',
    language: 'python',
    code: `from aurora_sdk import AuroraClient

client = AuroraClient()

# Run supply chain optimization
result = await client.quantum.run_scenario(
    scenario="supply_chain_optimization",
    num_suppliers=5,
    demand_variance=0.2,
    cost_weights=[0.3, 0.4, 0.2, 0.5, 0.3]
)

print(f"Optimal configuration: {result.optimal_state}")
print(f"Cost reduction: {result.metrics['cost_reduction']:.1f}%")
print(f"Reliability score: {result.metrics['reliability']:.2f}")
`,
    tags: ['quantum', 'optimization', 'beginner']
  },

  'decision/oracle': {
    title: 'Decision Oracle',
    description: 'Multi-criteria decision analysis',
    language: 'python',
    code: `from aurora_sdk import AuroraClient

client = AuroraClient()

# Multi-criteria decision analysis
result = await client.decision.oracle(
    options=[
        "Deploy to Cloud Provider A",
        "Deploy to Cloud Provider B",
        "Deploy to On-Premise"
    ],
    criteria={
        "cost": 0.4,
        "performance": 0.3,
        "security": 0.2,
        "reliability": 0.1
    },
    monte_carlo_samples=10000
)

# Show ranked results
for idx, option in enumerate(result.ranked_options, 1):
    print(f"{idx}. {option['name']}")
    print(f"   Confidence: {option['confidence']:.1%}")
`,
    tags: ['decision', 'monte-carlo', 'intermediate']
  },

  'memory/search': {
    title: 'Semantic Memory Search',
    description: 'Search memories with semantic understanding',
    language: 'python',
    code: `from aurora_sdk import AuroraClient

client = AuroraClient()

# Create some memories
await client.memory.create(
    "Quantum algorithms for optimization",
    tier="active",
    tags=["quantum", "algorithms"]
)

await client.memory.create(
    "Supply chain best practices",
    tier="active",
    tags=["supply-chain", "business"]
)

# Semantic search
results = await client.memory.search(
    query="optimization techniques",
    top_k=5
)

for memory in results:
    print(f"• {memory.content}")
    print(f"  Score: {memory.attention_score:.2f}")
    print(f"  Tags: {', '.join(memory.tags)}")
`,
    tags: ['memory', 'search', 'beginner']
  }
};
```

---

## 4. Backend Design

### 4.1 FastAPI Application

```python
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
import asyncio

app = FastAPI(title="Aurora Playground API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://playground.aurora.dev", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExecutionRequest(BaseModel):
    code: str
    language: Literal["python", "javascript"]
    session_id: str | None = None

class ExecutionResult(BaseModel):
    session_id: str
    output: list[str]
    error: str | None = None
    execution_time: float
    status: Literal["success", "error", "timeout"]

@app.post("/execute", response_model=ExecutionResult)
async def execute_code(request: ExecutionRequest):
    """Execute code in sandbox."""

    # Rate limiting check
    if not await check_rate_limit(request.session_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Create or get session
    session = await get_or_create_session(request.session_id)

    # Execute in sandbox
    executor = SandboxExecutor(request.language)
    result = await executor.execute(request.code, timeout=30)

    # Store in session
    await session.add_execution(result)

    return ExecutionResult(
        session_id=session.id,
        output=result.output,
        error=result.error,
        execution_time=result.execution_time,
        status=result.status
    )

@app.websocket("/ws/execute")
async def websocket_execute(websocket: WebSocket):
    """Execute code with streaming output via WebSocket."""
    await websocket.accept()

    try:
        while True:
            # Receive code
            data = await websocket.receive_json()

            # Execute with streaming
            executor = SandboxExecutor(data['language'])
            async for output in executor.execute_stream(data['code']):
                await websocket.send_json({
                    'type': 'output',
                    'data': output
                })

            # Send completion
            await websocket.send_json({
                'type': 'complete',
                'data': {'status': 'success'}
            })

    except Exception as e:
        await websocket.send_json({
            'type': 'error',
            'data': {'message': str(e)}
        })

@app.post("/share")
async def create_share_url(request: ExecutionRequest):
    """Create shareable URL."""

    # Create short code
    short_code = await create_short_code(request.code, request.language)

    return {
        'url': f"https://playground.aurora.dev/{short_code}",
        'short_code': short_code
    }

@app.get("/share/{short_code}")
async def get_shared_code(short_code: str):
    """Retrieve shared code."""

    data = await get_code_by_short_code(short_code)
    if not data:
        raise HTTPException(status_code=404, detail="Code not found")

    return data

@app.get("/examples")
async def list_examples():
    """List available examples."""
    return EXAMPLES
```

### 4.2 Sandbox Executor

```python
import docker
import asyncio
from typing import AsyncIterator

class SandboxExecutor:
    """Execute code in Docker sandbox."""

    def __init__(self, language: str):
        self.language = language
        self.client = docker.from_env()

    async def execute(self, code: str, timeout: int = 30) -> ExecutionResult:
        """Execute code and return result."""

        # Choose image
        image = self._get_image()

        # Create container
        container = await asyncio.to_thread(
            self.client.containers.create,
            image=image,
            command=self._get_command(code),
            mem_limit="512m",
            cpu_period=100000,
            cpu_quota=100000,  # 1 CPU core
            network_disabled=True,  # No network access
            read_only=True,  # Read-only root filesystem
            security_opt=["no-new-privileges"],
            cap_drop=["ALL"],
        )

        try:
            # Start container
            await asyncio.to_thread(container.start)

            # Wait with timeout
            result = await asyncio.wait_for(
                asyncio.to_thread(container.wait),
                timeout=timeout
            )

            # Get output
            output = await asyncio.to_thread(container.logs)

            return ExecutionResult(
                output=output.decode().split('\n'),
                error=None if result['StatusCode'] == 0 else "Execution failed",
                execution_time=result.get('Duration', 0),
                status='success' if result['StatusCode'] == 0 else 'error'
            )

        except asyncio.TimeoutError:
            return ExecutionResult(
                output=[],
                error="Execution timeout (30s limit)",
                execution_time=30.0,
                status='timeout'
            )

        finally:
            # Cleanup
            await asyncio.to_thread(container.remove, force=True)

    async def execute_stream(self, code: str) -> AsyncIterator[str]:
        """Execute code with streaming output."""
        # Similar to execute() but yield output lines as they arrive
        pass

    def _get_image(self) -> str:
        """Get Docker image for language."""
        return {
            'python': 'aurora-playground-python:latest',
            'javascript': 'aurora-playground-node:latest'
        }[self.language]

    def _get_command(self, code: str) -> list[str]:
        """Get command to execute code."""
        if self.language == 'python':
            return ['python', '-c', code]
        elif self.language == 'javascript':
            return ['node', '-e', code]
```

### 4.3 Session Management

```python
import redis
import uuid
from datetime import timedelta

class SessionManager:
    """Manage playground sessions."""

    def __init__(self):
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        self.ttl = timedelta(minutes=15)

    async def create_session(self) -> str:
        """Create new session."""
        session_id = str(uuid.uuid4())

        self.redis.setex(
            f"session:{session_id}",
            self.ttl,
            json.dumps({
                'created_at': datetime.now().isoformat(),
                'executions': []
            })
        )

        return session_id

    async def get_session(self, session_id: str) -> dict | None:
        """Get session data."""
        data = self.redis.get(f"session:{session_id}")
        return json.loads(data) if data else None

    async def add_execution(self, session_id: str, execution: dict):
        """Add execution to session."""
        session = await self.get_session(session_id)
        if session:
            session['executions'].append(execution)
            self.redis.setex(
                f"session:{session_id}",
                self.ttl,
                json.dumps(session)
            )
```

### 4.4 Rate Limiting

```python
from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/execute")
@limiter.limit("100/hour")  # 100 executions per hour per IP
async def execute_code(request: Request, exec_request: ExecutionRequest):
    # ... execution logic
    pass
```

---

## 5. Docker Images

### 5.1 Python Sandbox Image

```dockerfile
# Dockerfile.python
FROM python:3.11-slim

# Install aurora-sdk
RUN pip install --no-cache-dir aurora-sdk==0.1.0

# Create non-root user
RUN useradd -m -u 1000 sandbox

# Set working directory
WORKDIR /workspace

# Switch to non-root user
USER sandbox

# Default command
CMD ["python"]
```

### 5.2 Node.js Sandbox Image

```dockerfile
# Dockerfile.node
FROM node:20-slim

# Install @aurora/sdk
RUN npm install -g @aurora/sdk@0.1.0

# Create non-root user
RUN useradd -m -u 1000 sandbox

# Set working directory
WORKDIR /workspace

# Switch to non-root user
USER sandbox

# Default command
CMD ["node"]
```

---

## 6. Security

### 6.1 Sandbox Security

- **No network access:** Containers run with `network_disabled=True`
- **Read-only filesystem:** Root filesystem is read-only
- **Resource limits:** Memory (512MB), CPU (1 core), timeout (30s)
- **Drop capabilities:** `cap_drop=["ALL"]`
- **No privilege escalation:** `security_opt=["no-new-privileges"]`
- **Non-root user:** Code runs as user `sandbox` (UID 1000)

### 6.2 Input Validation

- Validate code length (max 50KB)
- Sanitize input
- No shell injection vulnerabilities

### 6.3 Rate Limiting

- 100 executions per hour per IP
- 10 concurrent executions per IP
- Monitor for abuse patterns

---

## 7. Monitoring & Analytics

### 7.1 Metrics

- Execution count (total, by language)
- Execution time (average, p95, p99)
- Success/failure rate
- Timeout rate
- Error types
- Popular examples

### 7.2 Logging

- All executions logged
- Error tracking (Sentry)
- Performance monitoring (APM)

---

## 8. Deployment

### 8.1 Infrastructure

**Frontend:**
- Hosting: Vercel
- CDN: Cloudflare
- Custom domain: playground.aurora.dev

**Backend:**
- Platform: AWS ECS or Google Cloud Run
- Load balancer: Application Load Balancer
- Session storage: Redis (ElastiCache)
- Container registry: ECR/GCR

**Scaling:**
- Frontend: Edge caching, CDN
- Backend: Auto-scaling based on CPU/memory
- Containers: Pre-warmed pool for fast startup

### 8.2 CI/CD

```yaml
# .github/workflows/deploy-playground.yml
name: Deploy Playground

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: vercel deploy --prod

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t playground-backend .
      - name: Push to registry
        run: docker push playground-backend
      - name: Deploy to ECS
        run: aws ecs update-service ...
```

---

## 9. Future Enhancements

- **Multiplayer:** Collaborative editing (CodeMirror, Yjs)
- **Jupyter integration:** Export to Jupyter notebooks
- **Version history:** Track code changes
- **AI assistance:** Code completion, suggestions
- **Templates:** Project templates, scaffolding
- **Notebooks:** Jupyter-style cells
- **Visualization:** Charts, graphs for results

---

**Status:** Ready for Implementation
**Next Steps:** Build frontend prototype with Monaco Editor
