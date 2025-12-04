import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Anchor, Code2, Info, Play, ShieldCheck } from 'lucide-react';

const scenarioGallery = [
  {
    id: 'quantum',
    title: 'Quantum continuity handshake',
    anchor: 'T1-QUANTUM-PLAY',
    language: 'python',
    tags: ['quantum', 'coherence', 'pii-redaction'],
    description: 'Run a coherence-aligned scenario with default PII masking and anchor metadata.',
    snippet: `# Anchor: T1-QUANTUM-PLAY
from aurora_sdk import AuroraClient

client = AuroraClient(api_key="sk_test_demo", base_url="http://localhost:8000")
quantum_session = await client.quantum.run_scenario(
    "coherence_alignment",
    anchor_seed="T1-QUANTUM-PLAY",
    session_metadata={
        "pii_redaction": {"enabled": True, "strategy": "mask", "fields": ["full_name", "email"]},
        "context_tag": "quantum_gallery"
    },
    qubits=4,
    depth=64
)`
  },
  {
    id: 'memory',
    title: 'Memory lane retention',
    anchor: 'T1-MEMORY-PLAY',
    language: 'python',
    tags: ['memory', 'semantic', 'pii-redaction'],
    description: 'Create a tiered memory with anchored metadata and automatic masking.',
    snippet: `# Anchor: T1-MEMORY-PLAY
from aurora_sdk import AuroraClient

client = AuroraClient(api_key="sk_test_demo")
secure_memory = await client.memory.create(
    "Decision lattice prototype",
    tier="active",
    tags=["memory", "research"],
    metadata={
        "anchor_seed": "T1-MEMORY-PLAY",
        "pii_redaction": {"enabled": True, "strategy": "mask", "fields": ["full_name"]}
    }
)`
  },
  {
    id: 'thread-bridge',
    title: 'Thread bridge transfer',
    anchor: 'T1-THREAD-BRIDGE',
    language: 'javascript',
    tags: ['bridge', 'session', 'pii-redaction'],
    description: 'Bridge a session across threads with continuity seals and redacted shares.',
    snippet: `// Anchor: T1-THREAD-BRIDGE
import { createSession, shareSession, forkSession } from '../../src/utils/session_flow.js';

const session = createSession({
  full_name: 'Quantum Trace',
  anchor_seed: 'T1-THREAD-BRIDGE'
});
const shared = shareSession(session);
const forked = forkSession(session, shared.shareToken);
console.log(shared.state.pii_redaction.strategy); // mask`
  },
  {
    id: 'decision',
    title: 'Decision audit run',
    anchor: 'T1-DECISION-PLAY',
    language: 'python',
    tags: ['decision', 'audit', 'pii-redaction'],
    description: 'Execute a decision gate with PII-safe telemetry and T1 anchors.',
    snippet: `# Anchor: T1-DECISION-PLAY
from src.integrations.chatgpt_agent_mode import ChatGPTAgentModeIntegration

agent = ChatGPTAgentModeIntegration()
create = await agent.execute_tool(
    "session_management",
    {"action": "create", "state_data": {"full_name": "Analyst Zero", "preference": "ethics"}}
)
run = await agent.execute_tool(
    "symbolic_processing",
    {"operation": "decision-gate", "data": {"threshold": 0.91}, "anchor_context": "T1-DECISION-PLAY"},
    session_id=create["result"]["session_id"]
)
share = await agent.execute_tool("session_management", {"action": "share", "session_id": create["result"]["session_id"]})`
  }
];

export default function Playground() {
  return (
    <div className="h-full p-8">
      <div className="mb-8">
        <h1 className="text-4xl font-display font-bold text-gradient">Developer Playground</h1>
        <p className="mt-2 text-gray-400">
          Interactive API exploration and code generation with anchored metadata and PII-aware defaults.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10">
        <Card className="glass-morphism lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Play className="h-5 w-5 text-accent-500" />
              <span>Try it in the playground</span>
            </CardTitle>
            <CardDescription>Spin up a session with T1 anchors and safe defaults.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <p className="text-sm text-gray-300">1) Start the dev server</p>
                <pre className="bg-black/30 rounded-lg p-3 text-xs text-gray-100 whitespace-pre-wrap border border-white/10">
{`npm install
npm run dev -- --host --port 5173`}
                </pre>
                <p className="text-xs text-gray-400">Visit http://localhost:5173/playground</p>
              </div>
              <div className="space-y-3">
                <div className="flex items-center space-x-2 text-sm text-gray-200">
                  <Anchor className="h-4 w-4 text-accent-500" />
                  <span>T1 anchors &amp; seeds</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-200">
                  <ShieldCheck className="h-4 w-4 text-accent-500" />
                  <span>PII redaction defaults enabled</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-200">
                  <Code2 className="h-4 w-4 text-accent-500" />
                  <span>Python &amp; JS snippets aligned with Aurora SDK</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-morphism">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Info className="h-5 w-5 text-accent-500" />
              <span>PII redaction defaults</span>
            </CardTitle>
            <CardDescription>Enabled across gallery scenarios.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <p className="text-sm text-gray-300">Masking strategy</p>
            <pre className="bg-black/30 rounded-lg p-3 text-xs text-gray-100 whitespace-pre-wrap border border-white/10">
{`{
  "enabled": true,
  "strategy": "mask",
  "fields": ["full_name", "email", "phone"]
}`}
            </pre>
            <p className="text-xs text-gray-400">
              Applied automatically in session creation, share, and fork paths.
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="mb-4">
        <h2 className="text-2xl font-semibold text-white">Starter scenario gallery</h2>
        <p className="text-sm text-gray-400">Quantum, memory, thread bridge, and decision anchors mapped to Aurora SDK patterns.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {scenarioGallery.map((scenario) => (
          <Card key={scenario.id} className="glass-morphism border border-white/10">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg text-white">{scenario.title}</CardTitle>
                <span className="text-xs text-accent-300 font-mono">{scenario.anchor}</span>
              </div>
              <CardDescription className="text-gray-300">{scenario.description}</CardDescription>
              <div className="flex flex-wrap gap-2 mt-2">
                {scenario.tags.map((tag) => (
                  <span key={tag} className="px-2 py-1 rounded-full bg-white/5 text-xs text-gray-200 border border-white/10">
                    {tag}
                  </span>
                ))}
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2 text-xs text-accent-200 mb-2">
                <ShieldCheck className="h-4 w-4" />
                <span>Metadata anchors + PII masking ({scenario.language})</span>
              </div>
              <pre className="bg-black/40 rounded-lg p-3 text-xs text-gray-100 whitespace-pre-wrap border border-white/10 leading-relaxed">
                {scenario.snippet}
              </pre>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
