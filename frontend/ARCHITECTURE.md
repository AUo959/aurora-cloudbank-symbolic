# Aurora Frontend Architecture
**Production-Grade Complex Systems Simulation Platform**

## Vision

Aurora is a cutting-edge platform enabling high-fidelity simulations of complex systems (institutional behavior, colony dynamics, social systems, astronomical phenomena, genomics). Researchers maintain perfect context via quantum memory, interact with Aurora as a research partner, and engage with Orion Station—a multi-agent research hub conducting autonomous experiments.

## Tech Stack

### Core Framework
- **React 18.2+** - Modern concurrent features, Suspense, streaming SSR
- **TypeScript 5.3+** - Full type safety across codebase
- **Vite 5.0+** - Lightning-fast HMR, optimized production builds

### UI & Styling
- **Tailwind CSS 3.4+** - Utility-first styling with custom design system
- **shadcn/ui** - High-quality, accessible component primitives
- **Radix UI** - Unstyled, accessible component foundation
- **Framer Motion** - Fluid animations and transitions
- **Lucide React** - Consistent icon system

### 3D Visualization
- **Three.js** - WebGL 3D graphics engine
- **React Three Fiber** - React renderer for Three.js
- **@react-three/drei** - Useful helpers for R3F
- **@react-three/postprocessing** - Post-processing effects

### Data Visualization
- **Recharts** - Declarative charting library
- **D3.js** - Advanced custom visualizations
- **visx** - Low-level visualization primitives

### State Management
- **Zustand** - Lightweight, scalable state management
- **React Query (TanStack Query)** - Server state, caching, synchronization
- **Jotai** - Atomic state management for complex forms

### Real-Time Communication
- **Socket.io Client** - WebSocket communication with Aurora API
- **EventSource** - Server-sent events for streaming updates

### API Integration
- **Axios** - HTTP client with interceptors
- **OpenAPI TypeScript Codegen** - Generate typed API client from OpenAPI spec

### Code Quality
- **ESLint** - Linting with TypeScript rules
- **Prettier** - Code formatting
- **Husky** - Git hooks for pre-commit quality checks
- **lint-staged** - Run linters on staged files

### Testing
- **Vitest** - Unit testing (Vite-native)
- **Testing Library** - Component testing
- **Playwright** - E2E testing
- **MSW** - API mocking

### Build & Deploy
- **Vite** - Build tool with optimizations
- **Vercel** - Deployment platform
- **Docker** - Containerization for self-hosting

## Application Architecture

### Directory Structure

```
frontend/
├── public/                      # Static assets
│   ├── favicon.ico
│   └── og-image.png
├── src/
│   ├── app/                     # Application root
│   │   ├── App.tsx              # Main app component
│   │   ├── router.tsx           # React Router configuration
│   │   └── providers.tsx        # Context providers
│   ├── pages/                   # Route pages
│   │   ├── Dashboard/           # System dashboard
│   │   ├── OrionStation/        # Multi-agent research hub
│   │   ├── Playground/          # Developer playground
│   │   ├── Simulations/         # Simulation management
│   │   └── Auth/                # Authentication pages
│   ├── features/                # Feature modules
│   │   ├── agent-console/       # AI Agent Console
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── api/
│   │   │   └── types/
│   │   ├── memory-viz/          # Memory Topology Visualizer
│   │   ├── compliance/          # Compliance Dashboard
│   │   ├── simulations/         # Simulation engine UI
│   │   └── orion/               # Orion Station features
│   ├── components/              # Shared components
│   │   ├── ui/                  # shadcn/ui components
│   │   ├── layout/              # Layout components
│   │   └── common/              # Common reusable components
│   ├── lib/                     # Utilities and configs
│   │   ├── api/                 # API client
│   │   ├── utils/               # Helper functions
│   │   └── constants/           # Constants
│   ├── hooks/                   # Shared hooks
│   ├── stores/                  # Zustand stores
│   ├── types/                   # TypeScript types
│   └── styles/                  # Global styles
├── tests/                       # Test files
├── .env.example                 # Environment variables template
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.ts
```

### Core Modules

#### 1. System Dashboard
**Purpose**: Central command center for Aurora platform

**Components**:
- **DashboardLayout** - Responsive grid layout
- **MetricsOverview** - System health, API usage, active simulations
- **QuickActions** - Start simulation, query memory, check compliance
- **ActivityFeed** - Real-time system events
- **ResourceMonitor** - CPU, memory, quantum backend status

**State**:
- Dashboard metrics (React Query)
- Real-time updates (Socket.io)
- User preferences (Zustand)

#### 2. AI Agent Console
**Purpose**: Interact with Aurora research partner with full transparency

**Features**:
- **Split-pane interface**: Chat (left) + System Internals (right)
- **Chat interface**: Message history, streaming responses
- **Memory retrieval visualization**: Which memories activated, relevance scores
- **Model selection display**: Show which model was chosen (Claude/GPT)
- **Ethics scoring**: Real-time compliance metrics
- **Drift detection**: Anomaly alerts

**Components**:
- `AgentChat` - Main chat interface
- `MessageList` - Virtualized message list
- `MessageInput` - Rich text input with markdown support
- `SystemInternals` - Real-time system state visualization
- `MemoryActivation` - Memory retrieval heatmap
- `EthicsMonitor` - Compliance scoring display

**Real-time Features**:
- WebSocket connection to `/ws/agent`
- Streaming message responses
- Live memory activation updates
- Drift detection alerts

#### 3. Memory Topology Visualizer
**Purpose**: 3D visualization of 56K quantum memory network

**Technology**: React Three Fiber, Three.js

**Features**:
- **3D Force-directed graph**: Memories as nodes, entanglement as edges
- **Color coding**: By importance (0-10 scale)
- **Size scaling**: Node size by memory weight
- **Quantum entanglement**: Animated edges showing correlation
- **Attention flow**: Particle effects showing memory retrieval
- **Interactive**: Click node to see memory details, zoom/pan/rotate
- **Filters**: By memory type, importance, tags, time range
- **Search**: Semantic search highlights relevant memories

**Components**:
- `MemoryScene` - Main Three.js scene
- `MemoryNode` - Individual memory visualization
- `EntanglementEdge` - Connection between memories
- `AttentionFlow` - Particle system for retrieval animation
- `MemoryDetails` - Side panel with memory metadata
- `MemoryControls` - Camera controls, filters, search

**Performance**:
- Level-of-detail (LOD) for rendering 56K nodes
- Octree spatial partitioning
- Instanced rendering for edges
- Web Workers for layout computation

#### 4. Compliance Dashboard
**Purpose**: Audit trails, PII detection, cryptographic verification

**Features**:
- **Audit Timeline**: Chronological view of all operations
- **PII Detection Demo**: Real-time redaction examples
- **Cryptographic Verification**: SHA-256 hash validation
- **Export Reports**: PDF compliance reports
- **DLP Tracking**: Context tag explorer
- **Ethics Engine**: Rule compliance matrix

**Components**:
- `AuditTimeline` - Interactive timeline with filtering
- `PIIDetector` - Live PII detection demo
- `CryptoVerifier` - Hash verification tool
- `ComplianceReport` - Exportable compliance summary
- `DLPExplorer` - Context tag and anchor visualization
- `EthicsMatrix` - Rule compliance heatmap

#### 5. Orion Station
**Purpose**: Multi-agent research hub with autonomous AI agents

**Concept**:
Orion Station is a persistent environment where multiple AI agents conduct research autonomously. Users can:
- Create research teams (multiple agents with specializations)
- Assign research objectives
- Monitor agent collaboration in real-time
- Review autonomous experiments
- Intervene or guide research direction

**Features**:
- **Agent Fleet View**: All active agents, their roles, current tasks
- **Research Board**: Kanban-style task board for research objectives
- **Experiment Monitor**: Live view of running experiments
- **Collaboration Graph**: Agent-to-agent communication network
- **Results Archive**: Completed research, findings, insights
- **Agent Console**: Direct communication with individual agents

**Components**:
- `StationOverview` - Bird's-eye view of all agent activity
- `AgentFleet` - Grid of agent cards with status
- `ResearchBoard` - Drag-and-drop task management
- `ExperimentRunner` - Real-time experiment monitoring
- `CollaborationViz` - Agent interaction network graph
- `AgentDialog` - Individual agent chat interface
- `ResearchTimeline` - Historical view of research progress

**Data Flow**:
- WebSocket connection for real-time agent updates
- Long-polling for experiment results
- Server-sent events for research milestones

#### 6. Developer Playground
**Purpose**: Interactive API exploration and code generation

**Features**:
- **API Explorer**: All Aurora endpoints with try-it-now interface
- **Code Generator**: Generate code in Python, JavaScript, cURL
- **Request Builder**: Visual query builder
- **Response Inspector**: JSON viewer with syntax highlighting
- **WebSocket Tester**: Test real-time connections
- **Example Gallery**: Pre-built examples for common use cases
- **API Key Management**: Generate, revoke, monitor usage

**Components**:
- `EndpointExplorer` - Browse all API endpoints
- `RequestBuilder` - Visual request configuration
- `CodeGenerator` - Multi-language code snippets
- `ResponseViewer` - Pretty JSON display
- `WebSocketTester` - Live WebSocket connection testing
- `ExampleGallery` - Curated examples with one-click run

**Examples**:
1. "Create a quantum-entangled memory"
2. "Run supply chain optimization simulation"
3. "Ask AI agent with memory retrieval"
4. "Detect PII in text"
5. "Query audit trail"
6. "Start multi-agent research task"

#### 7. Simulation Manager
**Purpose**: Create, configure, run, and analyze complex system simulations

**Simulation Types**:
- Institutional behavior modeling
- Colony/hive dynamics
- Social system dynamics
- Astronomical phenomena
- Genomic interactions
- Custom multi-agent systems

**Features**:
- **Simulation Builder**: Visual configuration of simulation parameters
- **Agent Designer**: Define agent types, behaviors, interactions
- **Environment Config**: Set up simulation space, rules, constraints
- **Real-time Monitor**: Live simulation state visualization
- **Results Analysis**: Charts, graphs, statistical analysis
- **Comparison Tool**: Compare simulation runs
- **Export**: Data export, video capture, report generation

**Components**:
- `SimulationBuilder` - Drag-and-drop simulation configuration
- `AgentDesigner` - Define agent archetypes
- `EnvironmentEditor` - Configure simulation environment
- `SimulationRunner` - Live simulation execution
- `ResultsViewer` - Multi-dimensional data visualization
- `ComparisonTool` - Side-by-side simulation comparison

## Design System

### Color Palette

**Primary** (Quantum Blue):
- `primary-50`: #eff6ff
- `primary-500`: #3b82f6
- `primary-900`: #1e3a8a

**Secondary** (Neural Purple):
- `secondary-50`: #faf5ff
- `secondary-500`: #a855f7
- `secondary-900`: #581c87

**Accent** (Aurora Cyan):
- `accent-50`: #ecfeff
- `accent-500`: #06b6d4
- `accent-900`: #164e63

**Semantic Colors**:
- `success`: #10b981 (green)
- `warning`: #f59e0b (amber)
- `error`: #ef4444 (red)
- `info`: #3b82f6 (blue)

**Neutral** (Dark theme base):
- `gray-50`: #f9fafb
- `gray-900`: #111827
- `gray-950`: #030712

### Typography

**Font Stack**:
- **Primary**: Inter (sans-serif)
- **Monospace**: JetBrains Mono (code)
- **Display**: Space Grotesk (headings)

**Type Scale**:
- `xs`: 0.75rem (12px)
- `sm`: 0.875rem (14px)
- `base`: 1rem (16px)
- `lg`: 1.125rem (18px)
- `xl`: 1.25rem (20px)
- `2xl`: 1.5rem (24px)
- `3xl`: 1.875rem (30px)
- `4xl`: 2.25rem (36px)

### Spacing System

8px base unit:
- `1`: 0.25rem (4px)
- `2`: 0.5rem (8px)
- `3`: 0.75rem (12px)
- `4`: 1rem (16px)
- `6`: 1.5rem (24px)
- `8`: 2rem (32px)
- `12`: 3rem (48px)
- `16`: 4rem (64px)

### Component Patterns

**Card**:
- Rounded corners (8px)
- Subtle shadow
- Hover state with elevation
- Dark background with border

**Button**:
- Primary: Solid fill, high contrast
- Secondary: Outline, lower contrast
- Ghost: Transparent, text only
- Loading state with spinner
- Disabled state (50% opacity)

**Input**:
- Clear focus ring
- Error state with message
- Helper text below
- Icon support (left/right)

**Modal**:
- Overlay backdrop (80% opacity)
- Center-aligned by default
- Close button (top-right)
- Keyboard accessible (Esc to close)

## Performance Optimization

### Code Splitting
- Route-based splitting (React.lazy)
- Component-level splitting for heavy components
- Dynamic imports for 3D visualizations

### Bundle Optimization
- Tree-shaking unused code
- Minification with Terser
- Gzip/Brotli compression
- CDN for static assets

### Rendering Optimization
- React.memo for pure components
- useMemo for expensive computations
- useCallback for stable references
- Virtualization for long lists (react-window)

### 3D Performance
- Frustum culling
- Level-of-detail (LOD)
- Instanced rendering
- Web Workers for physics

### Network Optimization
- React Query caching (stale-while-revalidate)
- Debounced API calls
- WebSocket connection pooling
- Lazy loading images

## Security

### Authentication
- JWT tokens in httpOnly cookies
- Refresh token rotation
- CSRF protection
- XSS prevention (sanitize user input)

### API Communication
- HTTPS only
- API key in Authorization header
- Rate limiting on client
- Request signing for sensitive operations

### Data Protection
- No sensitive data in localStorage
- PII masking in UI
- Secure WebSocket (wss://)
- Content Security Policy headers

## Accessibility

### WCAG 2.1 AA Compliance
- Semantic HTML
- ARIA labels for interactive elements
- Keyboard navigation (Tab, Enter, Escape)
- Focus management
- Screen reader support
- Color contrast ratios (4.5:1 minimum)

### Keyboard Shortcuts
- `Ctrl+K`: Command palette
- `Ctrl+/`: Toggle sidebar
- `Esc`: Close modal/dialog
- `Tab`: Navigate interactive elements
- `Space`: Activate button/checkbox

## Deployment

### Vercel (Primary)
- Automatic deployments on push
- Preview deployments for PRs
- Environment variables
- Edge network CDN

### Docker (Self-hosting)
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

### Environment Variables
- `VITE_API_BASE_URL` - Aurora API endpoint
- `VITE_WS_URL` - WebSocket endpoint
- `VITE_AUTH_DOMAIN` - Authentication domain
- `VITE_SENTRY_DSN` - Error tracking

## Monitoring & Analytics

### Error Tracking
- Sentry for error monitoring
- Source maps for production debugging
- User context for errors

### Analytics
- PostHog for product analytics
- Custom event tracking
- User journey funnels
- Performance monitoring (Web Vitals)

### Logging
- Structured logging with context
- Log levels (debug, info, warn, error)
- Console in dev, remote in production

## Development Workflow

### Getting Started
```bash
cd frontend
npm install
npm run dev  # Start dev server at http://localhost:5173
```

### Scripts
- `npm run dev` - Development server with HMR
- `npm run build` - Production build
- `npm run preview` - Preview production build
- `npm run lint` - Lint code with ESLint
- `npm run format` - Format code with Prettier
- `npm test` - Run tests with Vitest
- `npm run test:e2e` - Run E2E tests with Playwright
- `npm run type-check` - TypeScript type checking

### Git Workflow
1. Create feature branch: `git checkout -b feature/agent-console`
2. Make changes, commit frequently
3. Run checks: `npm run lint && npm run type-check && npm test`
4. Push and create PR
5. Automatic CI checks on PR
6. Merge after approval

## Testing Strategy

### Unit Tests (Vitest)
- Pure functions in `lib/utils`
- Custom hooks
- Store logic (Zustand)
- API client functions

### Component Tests (Testing Library)
- User interactions
- Conditional rendering
- Props validation
- Accessibility

### Integration Tests
- Feature workflows
- API integration
- WebSocket communication
- Multi-component interactions

### E2E Tests (Playwright)
- Critical user paths
- Authentication flow
- Simulation creation
- Report generation

## Future Enhancements

### Phase 2
- Mobile app (React Native)
- Offline mode (Service Workers)
- Multi-language support (i18n)
- Voice commands

### Phase 3
- VR/AR interface for 3D visualization
- Collaborative editing (CRDT)
- Plugin system for custom simulations
- Marketplace for simulation templates

---

**Version**: 1.0.0
**Last Updated**: 2025-11-22
**Author**: Aurora Frontend Team
