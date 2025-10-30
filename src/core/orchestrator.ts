/**
 * Constellation Orchestrator
 * Symbolic Anchor: T1_ORCHESTRATOR_PRIME
 * 
 * Manages task orchestration and execution across all constellation services
 */

import crypto from 'crypto';
import { EventEmitter } from 'events';

export type TaskPriority = 'high' | 'normal' | 'low';
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface Task {
  id: string;
  name: string;
  targetService: string;
  payload: any;
  priority: TaskPriority;
  status: TaskStatus;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  result?: any;
  error?: string;
  symbolicChain: string[];
}

export interface TaskExecutionContext {
  taskId: string;
  serviceName: string;
  timestamp: Date;
  anchor: string;
}

export interface MemorySnapshot {
  timestamp: Date;
  snapshotHash: string;
  tasks: {
    total: number;
    pending: number;
    running: number;
    completed: number;
    failed: number;
  };
  anchor: string;
}

export class Orchestrator extends EventEmitter {
  private tasks: Map<string, Task> = new Map();
  private taskQueue: {
    high: string[];
    normal: string[];
    low: string[];
  } = {
    high: [],
    normal: [],
    low: []
  };
  private runningTasks: Set<string> = new Set();
  private memorySnapshots: MemorySnapshot[] = [];
  private maxConcurrentTasks: number;
  private taskQueueSize: number;

  constructor(config: { maxConcurrentTasks: number; taskQueueSize: number }) {
    super();
    this.maxConcurrentTasks = config.maxConcurrentTasks;
    this.taskQueueSize = config.taskQueueSize;
  }

  /**
   * Submit a task to the orchestrator
   */
  submitTask(
    name: string,
    targetService: string,
    payload: any,
    priority: TaskPriority = 'normal',
    symbolicChain: string[] = []
  ): string {
    // Check queue size limit
    const totalQueued = this.taskQueue.high.length + this.taskQueue.normal.length + this.taskQueue.low.length;
    if (totalQueued >= this.taskQueueSize) {
      throw new Error(`[T1_ORCHESTRATOR_PRIME] Task queue is full (${this.taskQueueSize} tasks)`);
    }

    const taskId = this.generateTaskId();
    
    const task: Task = {
      id: taskId,
      name,
      targetService,
      payload,
      priority,
      status: 'pending',
      createdAt: new Date(),
      symbolicChain: [...symbolicChain, 'T1_ORCHESTRATOR_PRIME']
    };

    this.tasks.set(taskId, task);
    this.taskQueue[priority].push(taskId);

    console.log(`[T1_ORCHESTRATOR_PRIME] Task submitted: ${taskId} (${name}) -> ${targetService} [${priority}]`);
    this.emit('taskSubmitted', task);

    // Try to process tasks
    this.processTasks();

    return taskId;
  }

  /**
   * Process tasks from the queue
   */
  private async processTasks(): Promise<void> {
    // Check if we can run more tasks
    if (this.runningTasks.size >= this.maxConcurrentTasks) {
      return;
    }

    // Get next task by priority
    const taskId = this.getNextTask();
    if (!taskId) {
      return;
    }

    const task = this.tasks.get(taskId);
    if (!task) {
      return;
    }

    // Execute task
    await this.executeTask(task);

    // Process more tasks if capacity allows
    setTimeout(() => this.processTasks(), 0);
  }

  /**
   * Get next task from queue based on priority
   */
  private getNextTask(): string | null {
    // Check high priority first
    if (this.taskQueue.high.length > 0) {
      return this.taskQueue.high.shift()!;
    }
    
    // Then normal priority
    if (this.taskQueue.normal.length > 0) {
      return this.taskQueue.normal.shift()!;
    }
    
    // Finally low priority
    if (this.taskQueue.low.length > 0) {
      return this.taskQueue.low.shift()!;
    }

    return null;
  }

  /**
   * Execute a task
   */
  private async executeTask(task: Task): Promise<void> {
    this.runningTasks.add(task.id);
    task.status = 'running';
    task.startedAt = new Date();

    console.log(`[T1_ORCHESTRATOR_PRIME] Executing task: ${task.id} (${task.name})`);
    this.emit('taskStarted', task);

    try {
      // Create execution context
      const context: TaskExecutionContext = {
        taskId: task.id,
        serviceName: task.targetService,
        timestamp: new Date(),
        anchor: 'T1_ORCHESTRATOR_PRIME'
      };

      // Simulate task execution (in real implementation, would delegate to bridge)
      const result = await this.simulateTaskExecution(task, context);

      task.status = 'completed';
      task.completedAt = new Date();
      task.result = result;

      console.log(`[T1_ORCHESTRATOR_PRIME] Task completed: ${task.id}`);
      this.emit('taskCompleted', task);
    } catch (error) {
      task.status = 'failed';
      task.completedAt = new Date();
      task.error = error instanceof Error ? error.message : String(error);

      console.error(`[T1_ORCHESTRATOR_PRIME] Task failed: ${task.id}`, error);
      this.emit('taskFailed', task);
    } finally {
      this.runningTasks.delete(task.id);
    }
  }

  /**
   * Simulate task execution (stub for real bridge integration)
   */
  private async simulateTaskExecution(task: Task, context: TaskExecutionContext): Promise<any> {
    // In real implementation, would route to appropriate bridge
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          taskId: task.id,
          executedBy: task.targetService,
          timestamp: new Date().toISOString()
        });
      }, Math.random() * 1000 + 500);
    });
  }

  /**
   * Get task by ID
   */
  getTask(taskId: string): Task | undefined {
    return this.tasks.get(taskId);
  }

  /**
   * Get all tasks
   */
  getAllTasks(): Task[] {
    return Array.from(this.tasks.values());
  }

  /**
   * Get tasks by status
   */
  getTasksByStatus(status: TaskStatus): Task[] {
    return Array.from(this.tasks.values()).filter(task => task.status === status);
  }

  /**
   * Get tasks by service
   */
  getTasksByService(serviceName: string): Task[] {
    return Array.from(this.tasks.values()).filter(task => task.targetService === serviceName);
  }

  /**
   * Cancel a task
   */
  cancelTask(taskId: string): boolean {
    const task = this.tasks.get(taskId);
    if (!task) {
      return false;
    }

    if (task.status === 'running') {
      console.warn(`[T1_ORCHESTRATOR_PRIME] Cannot cancel running task: ${taskId}`);
      return false;
    }

    if (task.status === 'pending') {
      // Remove from queue
      const queue = this.taskQueue[task.priority];
      const index = queue.indexOf(taskId);
      if (index !== -1) {
        queue.splice(index, 1);
      }

      task.status = 'cancelled';
      task.completedAt = new Date();

      console.log(`[T1_ORCHESTRATOR_PRIME] Task cancelled: ${taskId}`);
      this.emit('taskCancelled', task);
      return true;
    }

    return false;
  }

  /**
   * Get queue statistics
   */
  getQueueStats(): {
    high: number;
    normal: number;
    low: number;
    running: number;
    total: number;
  } {
    return {
      high: this.taskQueue.high.length,
      normal: this.taskQueue.normal.length,
      low: this.taskQueue.low.length,
      running: this.runningTasks.size,
      total: this.taskQueue.high.length + this.taskQueue.normal.length + this.taskQueue.low.length + this.runningTasks.size
    };
  }

  /**
   * Create memory snapshot of orchestrator state
   */
  createMemorySnapshot(): MemorySnapshot {
    const tasks = Array.from(this.tasks.values());
    
    const snapshot: MemorySnapshot = {
      timestamp: new Date(),
      snapshotHash: this.generateSnapshotHash(tasks),
      tasks: {
        total: tasks.length,
        pending: tasks.filter(t => t.status === 'pending').length,
        running: tasks.filter(t => t.status === 'running').length,
        completed: tasks.filter(t => t.status === 'completed').length,
        failed: tasks.filter(t => t.status === 'failed').length
      },
      anchor: 'T1_ORCHESTRATOR_PRIME'
    };

    this.memorySnapshots.push(snapshot);
    console.log(`[T1_ORCHESTRATOR_PRIME] Memory snapshot created: ${snapshot.snapshotHash.substring(0, 16)}...`);

    return snapshot;
  }

  /**
   * Generate snapshot hash
   */
  private generateSnapshotHash(tasks: Task[]): string {
    const content = JSON.stringify({
      taskCount: tasks.length,
      statusCounts: {
        pending: tasks.filter(t => t.status === 'pending').length,
        running: tasks.filter(t => t.status === 'running').length,
        completed: tasks.filter(t => t.status === 'completed').length,
        failed: tasks.filter(t => t.status === 'failed').length
      },
      timestamp: new Date().toISOString()
    });
    
    return crypto.createHash('sha256').update(content).digest('hex');
  }

  /**
   * Get all memory snapshots
   */
  getMemorySnapshots(): MemorySnapshot[] {
    return [...this.memorySnapshots];
  }

  /**
   * Generate unique task ID
   */
  private generateTaskId(): string {
    return `task_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
  }

  /**
   * Get orchestrator statistics
   */
  getStats(): {
    totalTasks: number;
    queueStats: ReturnType<typeof this.getQueueStats>;
    taskStats: MemorySnapshot['tasks'];
  } {
    const tasks = Array.from(this.tasks.values());
    
    return {
      totalTasks: tasks.length,
      queueStats: this.getQueueStats(),
      taskStats: {
        total: tasks.length,
        pending: tasks.filter(t => t.status === 'pending').length,
        running: tasks.filter(t => t.status === 'running').length,
        completed: tasks.filter(t => t.status === 'completed').length,
        failed: tasks.filter(t => t.status === 'failed').length
      }
    };
  }
}
