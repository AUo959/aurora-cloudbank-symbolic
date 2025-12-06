import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { auroraAPI } from '@/lib/api/aurora';
import { formatDuration, getImportanceColor } from '@/lib/utils';
import type { AgentMessage, AgentResponse } from '@/types/aurora';
import { useMutation } from '@tanstack/react-query';
import {
  AlertTriangle,
  Bot,
  Brain,
  Coins,
  Database,
  Download,
  Send,
  Shield,
  ShieldAlert,
  Trash2,
  TrendingUp,
  User
} from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { toast } from 'sonner';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: AgentResponse;
  piiWarning?: boolean;
}

// PII detection patterns (client-side screening)
const PII_PATTERNS = {
  email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/gi,
  phone: /\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b/g,
  ssn: /\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b/g,
  creditCard: /\b(?:\d{4}[-\s]?){3}\d{4}\b/g,
  ipAddress: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g,
};

function detectPII(text: string): { hasPII: boolean; types: string[] } {
  const types: string[] = [];
  if (PII_PATTERNS.email.test(text)) types.push('email');
  if (PII_PATTERNS.phone.test(text)) types.push('phone');
  if (PII_PATTERNS.ssn.test(text)) types.push('SSN');
  if (PII_PATTERNS.creditCard.test(text)) types.push('credit card');
  if (PII_PATTERNS.ipAddress.test(text)) types.push('IP address');
  return { hasPII: types.length > 0, types };
}

// Session storage key for persistence
const STORAGE_KEY = 'aurora-agent-console-messages';
const TOKEN_USAGE_KEY = 'aurora-agent-console-tokens';

interface TokenUsageTotal {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  session_start: string;
}

export default function AgentConsole() {
  // Load persisted messages from session storage
  const loadPersistedMessages = (): Message[] => {
    try {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        return parsed.map((m: Message) => ({
          ...m,
          timestamp: new Date(m.timestamp),
        }));
      }
    } catch (e) {
      console.warn('Failed to load persisted messages:', e);
    }
    return [
      {
        id: '1',
        role: 'assistant',
        content:
          "Hello! I'm Aurora, your AI research partner. I have access to quantum memory, multi-model AI orchestration, and real-time compliance monitoring. How can I help you today?",
        timestamp: new Date(),
      },
    ];
  };

  const loadTokenUsage = (): TokenUsageTotal => {
    try {
      const stored = sessionStorage.getItem(TOKEN_USAGE_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch (e) {
      console.warn('Failed to load token usage:', e);
    }
    return {
      prompt_tokens: 0,
      completion_tokens: 0,
      total_tokens: 0,
      session_start: new Date().toISOString(),
    };
  };

  const [messages, setMessages] = useState<Message[]>(loadPersistedMessages);
  const [tokenUsage, setTokenUsage] = useState<TokenUsageTotal>(loadTokenUsage);
  const [input, setInput] = useState('');
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);
  const [showPIIWarning, setShowPIIWarning] = useState(false);
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Persist messages to session storage
  useEffect(() => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch (e) {
      console.warn('Failed to persist messages:', e);
    }
  }, [messages]);

  // Persist token usage
  useEffect(() => {
    try {
      sessionStorage.setItem(TOKEN_USAGE_KEY, JSON.stringify(tokenUsage));
    } catch (e) {
      console.warn('Failed to persist token usage:', e);
    }
  }, [tokenUsage]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const clearConversation = useCallback(() => {
    const confirmClear = window.confirm('Are you sure you want to clear the conversation? This cannot be undone.');
    if (confirmClear) {
      setMessages([
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: "Conversation cleared. I'm ready to start fresh. How can I help you?",
          timestamp: new Date(),
        },
      ]);
      setTokenUsage({
        prompt_tokens: 0,
        completion_tokens: 0,
        total_tokens: 0,
        session_start: new Date().toISOString(),
      });
      setSelectedMessage(null);
      toast.success('Conversation cleared');
    }
  }, []);

  const exportConversation = useCallback(() => {
    const exportData = {
      exported_at: new Date().toISOString(),
      messages: messages.map(m => ({
        role: m.role,
        content: m.content,
        timestamp: m.timestamp.toISOString(),
      })),
      token_usage: tokenUsage,
    };
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `aurora-conversation-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Conversation exported');
  }, [messages, tokenUsage]);

  const sendMessage = useMutation({
    mutationFn: (message: AgentMessage) => auroraAPI.agent.chat(message),
    onSuccess: (data: AgentResponse, variables) => {
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        metadata: data,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setSelectedMessage(assistantMessage);

      // Update token usage
      if (data.token_usage) {
        setTokenUsage(prev => ({
          ...prev,
          prompt_tokens: prev.prompt_tokens + (data.token_usage?.prompt_tokens || 0),
          completion_tokens: prev.completion_tokens + (data.token_usage?.completion_tokens || 0),
          total_tokens: prev.total_tokens + (data.token_usage?.total_tokens || 0),
        }));
      }
    },
    onError: (error) => {
      toast.error('Failed to send message', {
        description: error instanceof Error ? error.message : 'Unknown error',
      });
    },
  });

  const handleSend = useCallback((bypassPIICheck = false) => {
    const messageText = pendingMessage || input;
    if (!messageText.trim()) return;

    // PII detection (unless bypassed)
    if (!bypassPIICheck) {
      const piiCheck = detectPII(messageText);
      if (piiCheck.hasPII) {
        setPendingMessage(messageText);
        setShowPIIWarning(true);
        toast.warning(`Potential PII detected: ${piiCheck.types.join(', ')}`, {
          description: 'Please confirm you want to send this message.',
        });
        return;
      }
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
      piiWarning: bypassPIICheck,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setPendingMessage(null);
    setShowPIIWarning(false);

    sendMessage.mutate({
      content: messageText,
      role: 'user',
      use_memory: true,
    });
  }, [input, pendingMessage, sendMessage]);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const cancelPIIMessage = useCallback(() => {
    setPendingMessage(null);
    setShowPIIWarning(false);
  }, []);

  return (
    <div className="flex h-full">
      {/* Chat Panel - Left */}
      <div className="flex flex-1 flex-col border-r border-white/10">
        {/* Header with session controls */}
        <div className="border-b border-white/10 bg-black/20 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-display font-bold text-gradient flex items-center space-x-2">
                <Bot className="h-6 w-6" aria-hidden="true" />
                <span>AI Agent Console</span>
              </h1>
              <p className="mt-1 text-sm text-gray-400">
                Chat with Aurora research partner • Full system transparency
              </p>
            </div>
            <div className="flex items-center space-x-2">
              {/* Token usage display */}
              <div className="flex items-center space-x-1 text-xs text-gray-400 bg-white/5 rounded-lg px-3 py-2" role="status" aria-label="Session token usage">
                <Coins className="h-3 w-3 text-accent-400" aria-hidden="true" />
                <span className="font-mono">{tokenUsage.total_tokens.toLocaleString()}</span>
                <span>tokens</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={exportConversation}
                className="text-gray-400 hover:text-white"
                title="Export conversation"
                aria-label="Export conversation as JSON"
              >
                <Download className="h-4 w-4" aria-hidden="true" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearConversation}
                className="text-gray-400 hover:text-red-400"
                title="Clear conversation"
                aria-label="Clear conversation history"
              >
                <Trash2 className="h-4 w-4" aria-hidden="true" />
              </Button>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 space-y-4 overflow-y-auto p-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              onClick={() => message.metadata && setSelectedMessage(message)}
            >
              <div
                className={`flex max-w-[80%] space-x-3 ${message.role === 'assistant' ? 'cursor-pointer hover:opacity-80' : ''}`}
              >
                {message.role === 'assistant' && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-500/20">
                    <Bot className="h-4 w-4 text-primary-400" />
                  </div>
                )}
                <div
                  className={`rounded-lg px-4 py-3 ${message.role === 'user'
                      ? 'bg-primary-500/20 text-white'
                      : 'glass-morphism text-gray-200'
                    }`}
                >
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
                  {message.metadata && (
                    <div className="mt-2 flex items-center space-x-3 text-xs text-gray-500">
                      <span className="flex items-center space-x-1">
                        <Brain className="h-3 w-3" />
                        <span>{message.metadata.model_used}</span>
                      </span>
                      <span>•</span>
                      <span>{formatDuration(message.metadata.generation_time_ms)}</span>
                      {message.metadata.memory_retrieval && (
                        <>
                          <span>•</span>
                          <span className="flex items-center space-x-1">
                            <Database className="h-3 w-3" />
                            <span>{message.metadata.memory_retrieval.memories_retrieved} memories</span>
                          </span>
                        </>
                      )}
                    </div>
                  )}
                </div>
                {message.role === 'user' && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-accent-500/20">
                    <User className="h-4 w-4 text-accent-400" />
                  </div>
                )}
              </div>
            </div>
          ))}
          {sendMessage.isPending && (
            <div className="flex justify-start">
              <div className="flex space-x-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-500/20">
                  <Bot className="h-4 w-4 text-primary-400 animate-pulse" />
                </div>
                <div className="glass-morphism rounded-lg px-4 py-3">
                  <div className="flex space-x-2">
                    <div className="h-2 w-2 animate-bounce rounded-full bg-primary-500" />
                    <div className="h-2 w-2 animate-bounce rounded-full bg-primary-500 [animation-delay:0.2s]" />
                    <div className="h-2 w-2 animate-bounce rounded-full bg-primary-500 [animation-delay:0.4s]" />
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-white/10 bg-black/20 p-4">
          {/* PII Warning Banner */}
          {showPIIWarning && (
            <div className="mb-3 flex items-center justify-between rounded-lg bg-yellow-500/20 border border-yellow-500/30 px-4 py-3" role="alert">
              <div className="flex items-center space-x-2">
                <ShieldAlert className="h-5 w-5 text-yellow-400" aria-hidden="true" />
                <span className="text-sm text-yellow-200">
                  Potential sensitive information detected. Send anyway?
                </span>
              </div>
              <div className="flex space-x-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={cancelPIIMessage}
                  className="text-gray-400 hover:text-white"
                >
                  Cancel
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSend(true)}
                  className="border-yellow-500/50 text-yellow-400 hover:bg-yellow-500/20"
                >
                  Send Anyway
                </Button>
              </div>
            </div>
          )}
          <div className="flex space-x-2">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask Aurora anything..."
              className="flex-1 resize-none rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-sm text-white placeholder-gray-500 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50"
              rows={3}
              disabled={sendMessage.isPending}
              aria-label="Message input"
            />
            <Button
              onClick={() => handleSend()}
              disabled={!input.trim() || sendMessage.isPending}
              variant="quantum"
              size="icon"
              className="h-auto"
              aria-label="Send message"
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* System Internals - Right */}
      <div className="w-96 overflow-y-auto bg-black/20 p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-200">System Internals</h2>

        {selectedMessage?.metadata ? (
          <div className="space-y-4">
            {/* Model Selection */}
            <Card className="glass-morphism">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center space-x-2 text-sm">
                  <Brain className="h-4 w-4 text-secondary-500" />
                  <span>Model Selection</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-400">Selected Model</span>
                    <span className="text-sm font-mono text-secondary-400">
                      {selectedMessage.metadata.model_used}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-400">Generation Time</span>
                    <span className="text-sm font-mono text-accent-400">
                      {formatDuration(selectedMessage.metadata.generation_time_ms)}
                    </span>
                  </div>
                  {selectedMessage.metadata.token_usage && (
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-400">Tokens Used</span>
                      <span className="text-sm font-mono text-primary-400">
                        {selectedMessage.metadata.token_usage.total_tokens}
                      </span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Memory Retrieval */}
            {selectedMessage.metadata.memory_retrieval && (
              <Card className="glass-morphism">
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center space-x-2 text-sm">
                    <Database className="h-4 w-4 text-primary-500" />
                    <span>Memory Retrieval</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-400">Memories Retrieved</span>
                      <span className="text-sm font-mono text-primary-400">
                        {selectedMessage.metadata.memory_retrieval.memories_retrieved}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-400">Retrieval Time</span>
                      <span className="text-sm font-mono text-accent-400">
                        {formatDuration(selectedMessage.metadata.memory_retrieval.retrieval_time_ms)}
                      </span>
                    </div>
                    {selectedMessage.metadata.memory_retrieval.relevant_memories.length > 0 && (
                      <div className="space-y-2">
                        <p className="text-xs text-gray-400">Top Memories:</p>
                        {selectedMessage.metadata.memory_retrieval.relevant_memories
                          .slice(0, 3)
                          .map((mem) => (
                            <div
                              key={mem.id}
                              className="rounded border border-white/10 bg-white/5 p-2"
                            >
                              <div className="flex items-center justify-between">
                                <span className="text-xs font-mono text-gray-400">
                                  {mem.id.slice(0, 8)}...
                                </span>
                                <div
                                  className="h-2 w-2 rounded-full"
                                  style={{
                                    backgroundColor: getImportanceColor(mem.importance),
                                  }}
                                />
                              </div>
                              <p className="mt-1 text-xs text-gray-500">
                                {mem.tags.join(', ')}
                              </p>
                            </div>
                          ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Ethics & Compliance */}
            {selectedMessage.metadata.ethics_score && (
              <Card className="glass-morphism">
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center space-x-2 text-sm">
                    <Shield className="h-4 w-4 text-success" />
                    <span>Ethics & Compliance</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-400">Alignment Score</span>
                        <span className="text-success font-semibold">
                          {(selectedMessage.metadata.ethics_score.alignment_score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-gray-700">
                        <div
                          className="h-full bg-success transition-all"
                          style={{
                            width: `${selectedMessage.metadata.ethics_score.alignment_score * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-400">Safety Score</span>
                        <span className="text-primary-400 font-semibold">
                          {(selectedMessage.metadata.ethics_score.safety_score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-gray-700">
                        <div
                          className="h-full bg-primary-500 transition-all"
                          style={{
                            width: `${selectedMessage.metadata.ethics_score.safety_score * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-400">Transparency Level</span>
                      <span className="text-sm font-mono text-accent-400 capitalize">
                        {selectedMessage.metadata.ethics_score.transparency_level}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Drift Detection */}
            {selectedMessage.metadata.drift_detected !== undefined && (
              <Card
                className={`glass-morphism ${selectedMessage.metadata.drift_detected ? 'border-warning' : ''}`}
              >
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center space-x-2 text-sm">
                    <TrendingUp
                      className={`h-4 w-4 ${selectedMessage.metadata.drift_detected ? 'text-warning' : 'text-success'}`}
                    />
                    <span>Drift Detection</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {selectedMessage.metadata.drift_detected ? (
                    <div className="flex items-center space-x-2">
                      <AlertTriangle className="h-4 w-4 text-warning" />
                      <span className="text-sm text-warning">Behavioral drift detected</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-4 w-4 text-success" />
                      <span className="text-sm text-success">Operating within baseline</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        ) : (
          <div className="flex h-64 items-center justify-center">
            <div className="text-center text-gray-500">
              <Brain className="mx-auto h-12 w-12 opacity-50" />
              <p className="mt-4 text-sm">Select a message to view system internals</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
