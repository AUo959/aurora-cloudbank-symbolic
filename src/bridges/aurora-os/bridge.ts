/**
 * AuroraOS Bridge Implementation
 * Symbolic Anchor: T1_AURORA_BRIDGE
 * 
 * WebSocket-based bridge for communication with AuroraOS runtime
 */

import { EventEmitter } from 'events';
import WebSocket from 'ws';

export interface AuroraOSMessage {
  type: 'module' | 'agent' | 'event' | 'health' | 'response';
  id?: string;
  payload: any;
  timestamp: string;
  anchor: string;
}

export interface AuroraOSConfig {
  endpoint: string;
  reconnectInterval: number;
  maxReconnectAttempts: number;
}

export class AuroraOSBridge extends EventEmitter {
  private ws: WebSocket | null = null;
  private connected: boolean = false;
  private reconnectAttempts: number = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private pendingMessages: Map<string, { resolve: Function; reject: Function }> = new Map();

  constructor(private config: AuroraOSConfig) {
    super();
  }

  /**
   * Connect to AuroraOS
   */
  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      console.log(`[T1_AURORA_BRIDGE] Connecting to AuroraOS at ${this.config.endpoint}`);

      try {
        this.ws = new WebSocket(this.config.endpoint);

        this.ws.on('open', () => {
          console.log('[T1_AURORA_BRIDGE] Connected to AuroraOS');
          this.connected = true;
          this.reconnectAttempts = 0;
          this.emit('connected');
          resolve();
        });

        this.ws.on('message', (data: Buffer) => {
          this.handleMessage(data.toString());
        });

        this.ws.on('close', () => {
          console.log('[T1_AURORA_BRIDGE] Connection to AuroraOS closed');
          this.connected = false;
          this.emit('disconnected');
          this.attemptReconnect();
        });

        this.ws.on('error', (error) => {
          console.error('[T1_AURORA_BRIDGE] WebSocket error:', error);
          this.emit('error', error);
          if (!this.connected) {
            reject(error);
          }
        });
      } catch (error) {
        console.error('[T1_AURORA_BRIDGE] Failed to create WebSocket:', error);
        reject(error);
      }
    });
  }

  /**
   * Disconnect from AuroraOS
   */
  async disconnect(): Promise<void> {
    console.log('[T1_AURORA_BRIDGE] Disconnecting from AuroraOS');
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.connected = false;
  }

  /**
   * Attempt to reconnect
   */
  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.error(`[T1_AURORA_BRIDGE] Max reconnect attempts (${this.config.maxReconnectAttempts}) reached`);
      this.emit('reconnectFailed');
      return;
    }

    this.reconnectAttempts++;
    console.log(`[T1_AURORA_BRIDGE] Reconnect attempt ${this.reconnectAttempts}/${this.config.maxReconnectAttempts}`);

    this.reconnectTimer = setTimeout(() => {
      this.connect().catch((error) => {
        console.error('[T1_AURORA_BRIDGE] Reconnect failed:', error);
      });
    }, this.config.reconnectInterval);
  }

  /**
   * Handle incoming message
   */
  private handleMessage(data: string): void {
    try {
      const message: AuroraOSMessage = JSON.parse(data);
      
      console.log(`[T1_AURORA_BRIDGE] Received message: ${message.type} ${message.id || ''}`);
      
      // Handle response to pending request
      if (message.type === 'response' && message.id) {
        const pending = this.pendingMessages.get(message.id);
        if (pending) {
          pending.resolve(message.payload);
          this.pendingMessages.delete(message.id);
          return;
        }
      }

      // Emit event for listeners
      this.emit('message', message);
      this.emit(message.type, message);
    } catch (error) {
      console.error('[T1_AURORA_BRIDGE] Failed to parse message:', error);
      this.emit('parseError', error);
    }
  }

  /**
   * Send message to AuroraOS
   */
  private sendMessage(message: AuroraOSMessage): void {
    if (!this.connected || !this.ws) {
      throw new Error('[T1_AURORA_BRIDGE] Not connected to AuroraOS');
    }

    const data = JSON.stringify(message);
    this.ws.send(data);
  }

  /**
   * Execute a module on AuroraOS
   */
  async executeModule(moduleName: string, params: any = {}): Promise<any> {
    const message: AuroraOSMessage = {
      type: 'module',
      id: this.generateMessageId(),
      payload: {
        module: moduleName,
        params
      },
      timestamp: new Date().toISOString(),
      anchor: 'T1_AURORA_BRIDGE'
    };

    return this.sendRequest(message);
  }

  /**
   * Execute an agent on AuroraOS
   */
  async executeAgent(agentName: string, task: any): Promise<any> {
    const message: AuroraOSMessage = {
      type: 'agent',
      id: this.generateMessageId(),
      payload: {
        agent: agentName,
        task
      },
      timestamp: new Date().toISOString(),
      anchor: 'T1_AURORA_BRIDGE'
    };

    return this.sendRequest(message);
  }

  /**
   * Check AuroraOS health
   */
  async checkHealth(): Promise<any> {
    const message: AuroraOSMessage = {
      type: 'health',
      id: this.generateMessageId(),
      payload: {},
      timestamp: new Date().toISOString(),
      anchor: 'T1_AURORA_BRIDGE'
    };

    return this.sendRequest(message);
  }

  /**
   * Send request and wait for response
   */
  private sendRequest(message: AuroraOSMessage): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!message.id) {
        reject(new Error('Message ID is required for requests'));
        return;
      }

      // Store pending request
      this.pendingMessages.set(message.id, { resolve, reject });

      // Set timeout for response
      const timeout = setTimeout(() => {
        this.pendingMessages.delete(message.id!);
        reject(new Error(`[T1_AURORA_BRIDGE] Request timeout for ${message.id}`));
      }, 30000); // 30 second timeout

      // Send message
      try {
        this.sendMessage(message);
      } catch (error) {
        clearTimeout(timeout);
        this.pendingMessages.delete(message.id);
        reject(error);
      }
    });
  }

  /**
   * Generate unique message ID
   */
  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.connected;
  }

  /**
   * Get connection stats
   */
  getStats(): {
    connected: boolean;
    reconnectAttempts: number;
    pendingMessages: number;
  } {
    return {
      connected: this.connected,
      reconnectAttempts: this.reconnectAttempts,
      pendingMessages: this.pendingMessages.size
    };
  }
}
