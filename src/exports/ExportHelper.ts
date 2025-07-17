/**
 * Aurora/GUMAS Export Utilities
 * Multi-format data export with integrity validation
 * Operator: AUo959
 */

import * as crypto from 'crypto';
import * as fs from 'fs';
import * as path from 'path';

export type ExportFormat = 'json' | 'yaml' | 'binary' | 'encrypted';

export interface ExportManifest {
  id: string;
  operatorId: string;
  timestamp: Date;
  format: ExportFormat;
  compression: boolean;
  encryption: boolean;
  files: ExportFileInfo[];
  metadata: Record<string, any>;
  integrity: {
    checksum: string;
    signature: string;
    algorithm: string;
  };
  compliance: {
    auroraStandard: string;
    gumasCompliant: boolean;
    operatorTraceability: boolean;
  };
}

export interface ExportFileInfo {
  filename: string;
  size: number;
  checksum: string;
  contentType: string;
  compressed: boolean;
  encrypted: boolean;
}

export interface ExportOptions {
  format: ExportFormat;
  compress?: boolean;
  encrypt?: boolean;
  includeMetadata?: boolean;
  outputDirectory?: string;
  filename?: string;
  encryptionKey?: string;
}

export interface ExportResult {
  success: boolean;
  manifest: ExportManifest;
  outputPath: string;
  files: string[];
  errors?: string[];
}

/**
 * Export helper for multi-format data packaging
 */
export class ExportHelper {
  private readonly operatorId = 'AUo959';
  private readonly auroraStandard = '2024.1';

  /**
   * Export data in specified format
   */
  async exportData(data: any, options: ExportOptions): Promise<ExportResult> {
    const exportId = this.generateExportId();
    const timestamp = new Date();
    const outputDir = options.outputDirectory || './exports';
    
    // Ensure output directory exists
    await this.ensureDirectory(outputDir);

    const errors: string[] = [];
    const files: string[] = [];

    try {
      // Generate filename if not provided
      const filename = options.filename || this.generateFilename(exportId, options.format);
      const outputPath = path.join(outputDir, filename);

      // Process data based on format
      let processedData: Buffer;
      let contentType: string;

      switch (options.format) {
        case 'json':
          processedData = await this.processJsonExport(data, options);
          contentType = 'application/json';
          break;
        case 'yaml':
          processedData = await this.processYamlExport(data, options);
          contentType = 'application/yaml';
          break;
        case 'binary':
          processedData = await this.processBinaryExport(data, options);
          contentType = 'application/octet-stream';
          break;
        case 'encrypted':
          processedData = await this.processEncryptedExport(data, options);
          contentType = 'application/encrypted';
          break;
        default:
          throw new Error(`Unsupported export format: ${options.format}`);
      }

      // Apply compression if requested
      if (options.compress) {
        processedData = await this.compressData(processedData);
      }

      // Write to file
      await fs.promises.writeFile(outputPath, processedData);
      files.push(outputPath);

      // Create file info
      const fileInfo: ExportFileInfo = {
        filename: path.basename(outputPath),
        size: processedData.length,
        checksum: this.calculateChecksum(processedData),
        contentType,
        compressed: options.compress || false,
        encrypted: options.encrypt || options.format === 'encrypted'
      };

      // Create manifest
      const manifest = await this.createManifest(exportId, timestamp, options, [fileInfo], data);

      // Write manifest
      const manifestPath = path.join(outputDir, `manifest_${exportId}.json`);
      await fs.promises.writeFile(manifestPath, JSON.stringify(manifest, null, 2));
      files.push(manifestPath);

      return {
        success: true,
        manifest,
        outputPath,
        files,
        errors: errors.length > 0 ? errors : undefined
      };

    } catch (error) {
      errors.push(`Export failed: ${error instanceof Error ? error.message : String(error)}`);
      
      return {
        success: false,
        manifest: {} as ExportManifest,
        outputPath: '',
        files,
        errors
      };
    }
  }

  /**
   * Export multiple datasets with batch processing
   */
  async batchExport(datasets: Array<{ data: any; name: string; options: ExportOptions }>): Promise<ExportResult[]> {
    const results: ExportResult[] = [];

    for (const dataset of datasets) {
      const modifiedOptions = {
        ...dataset.options,
        filename: dataset.options.filename || `${dataset.name}_${Date.now()}.${dataset.options.format}`
      };

      const result = await this.exportData(dataset.data, modifiedOptions);
      results.push(result);
    }

    return results;
  }

  /**
   * Import data from exported file
   */
  async importData(manifestPath: string, encryptionKey?: string): Promise<any> {
    // Read manifest
    const manifestData = await fs.promises.readFile(manifestPath, 'utf8');
    const manifest: ExportManifest = JSON.parse(manifestData);

    // Verify manifest integrity
    if (!await this.verifyManifest(manifest, manifestPath)) {
      throw new Error('Manifest integrity verification failed');
    }

    const manifestDir = path.dirname(manifestPath);
    const dataFile = manifest.files[0]; // Assuming single data file for simplicity

    if (!dataFile) {
      throw new Error('No data file found in manifest');
    }

    const dataPath = path.join(manifestDir, dataFile.filename);
    let data = await fs.promises.readFile(dataPath);

    // Verify file integrity
    const calculatedChecksum = this.calculateChecksum(data);
    if (calculatedChecksum !== dataFile.checksum) {
      throw new Error('Data file integrity verification failed');
    }

    // Decompress if needed
    if (dataFile.compressed) {
      data = await this.decompressData(data);
    }

    // Process based on format
    switch (manifest.format) {
      case 'json':
        return JSON.parse(data.toString('utf8'));
      case 'yaml':
        return this.parseYaml(data.toString('utf8'));
      case 'binary':
        return this.parseBinary(data);
      case 'encrypted':
        if (!encryptionKey) {
          throw new Error('Encryption key required for encrypted export');
        }
        return await this.decryptAndParse(data, encryptionKey);
      default:
        throw new Error(`Unsupported import format: ${manifest.format}`);
    }
  }

  /**
   * Validate export integrity
   */
  async validateExport(manifestPath: string): Promise<boolean> {
    try {
      const manifestData = await fs.promises.readFile(manifestPath, 'utf8');
      const manifest: ExportManifest = JSON.parse(manifestData);

      return await this.verifyManifest(manifest, manifestPath);
    } catch {
      return false;
    }
  }

  /**
   * List exports in directory
   */
  async listExports(directory: string = './exports'): Promise<ExportManifest[]> {
    const manifests: ExportManifest[] = [];

    try {
      const files = await fs.promises.readdir(directory);
      const manifestFiles = files.filter(f => f.startsWith('manifest_') && f.endsWith('.json'));

      for (const manifestFile of manifestFiles) {
        try {
          const manifestPath = path.join(directory, manifestFile);
          const manifestData = await fs.promises.readFile(manifestPath, 'utf8');
          const manifest: ExportManifest = JSON.parse(manifestData);
          manifests.push(manifest);
        } catch {
          // Skip invalid manifests
        }
      }
    } catch {
      // Directory doesn't exist or can't be read
    }

    return manifests.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  }

  private async processJsonExport(data: any, options: ExportOptions): Promise<Buffer> {
    const jsonData = options.includeMetadata !== false ? this.addMetadata(data) : data;
    return Buffer.from(JSON.stringify(jsonData, null, 2), 'utf8');
  }

  private async processYamlExport(data: any, options: ExportOptions): Promise<Buffer> {
    const yamlData = options.includeMetadata !== false ? this.addMetadata(data) : data;
    // Simple YAML serialization - in production, use a proper YAML library
    const yamlString = this.toYaml(yamlData);
    return Buffer.from(yamlString, 'utf8');
  }

  private async processBinaryExport(data: any, options: ExportOptions): Promise<Buffer> {
    const dataWithMetadata = options.includeMetadata !== false ? this.addMetadata(data) : data;
    // Simple binary serialization using JSON as intermediate
    const jsonString = JSON.stringify(dataWithMetadata);
    return Buffer.from(jsonString, 'utf8');
  }

  private async processEncryptedExport(data: any, options: ExportOptions): Promise<Buffer> {
    const dataWithMetadata = options.includeMetadata !== false ? this.addMetadata(data) : data;
    const jsonString = JSON.stringify(dataWithMetadata);
    
    const key = options.encryptionKey || this.generateEncryptionKey();
    return this.encrypt(Buffer.from(jsonString, 'utf8'), key);
  }

  private async compressData(data: Buffer): Promise<Buffer> {
    const zlib = require('zlib');
    return new Promise((resolve, reject) => {
      zlib.gzip(data, (err: Error | null, result: Buffer) => {
        if (err) reject(err);
        else resolve(result);
      });
    });
  }

  private async decompressData(data: Buffer): Promise<Buffer> {
    const zlib = require('zlib');
    return new Promise((resolve, reject) => {
      zlib.gunzip(data, (err: Error | null, result: Buffer) => {
        if (err) reject(err);
        else resolve(result);
      });
    });
  }

  private encrypt(data: Buffer, key: string): Buffer {
    const algorithm = 'aes-256-gcm';
    const iv = crypto.randomBytes(16);
    const keyBuffer = crypto.scryptSync(key, 'aurora-salt', 32);
    
    const cipher = crypto.createCipheriv(algorithm, keyBuffer, iv);
    const encrypted = Buffer.concat([cipher.update(data), cipher.final()]);
    const authTag = cipher.getAuthTag();
    
    return Buffer.concat([iv, authTag, encrypted]);
  }

  private decrypt(encryptedData: Buffer, key: string): Buffer {
    const algorithm = 'aes-256-gcm';
    const keyBuffer = crypto.scryptSync(key, 'aurora-salt', 32);
    
    const iv = encryptedData.subarray(0, 16);
    const authTag = encryptedData.subarray(16, 32);
    const encrypted = encryptedData.subarray(32);
    
    const decipher = crypto.createDecipheriv(algorithm, keyBuffer, iv);
    decipher.setAuthTag(authTag);
    
    return Buffer.concat([decipher.update(encrypted), decipher.final()]);
  }

  private async decryptAndParse(data: Buffer, key: string): Promise<any> {
    const decrypted = this.decrypt(data, key);
    return JSON.parse(decrypted.toString('utf8'));
  }

  private addMetadata(data: any): any {
    return {
      auroraExport: {
        operatorId: this.operatorId,
        exportedAt: new Date(),
        standard: this.auroraStandard,
        gumasCompliant: true
      },
      data
    };
  }

  private async createManifest(
    exportId: string,
    timestamp: Date,
    options: ExportOptions,
    files: ExportFileInfo[],
    originalData: any
  ): Promise<ExportManifest> {
    const dataChecksum = this.calculateChecksum(Buffer.from(JSON.stringify(originalData)));
    
    return {
      id: exportId,
      operatorId: this.operatorId,
      timestamp,
      format: options.format,
      compression: options.compress || false,
      encryption: options.encrypt || options.format === 'encrypted',
      files,
      metadata: {
        originalDataSize: JSON.stringify(originalData).length,
        exportOptions: options,
        auroraStandard: this.auroraStandard
      },
      integrity: {
        checksum: dataChecksum,
        signature: this.generateSignature(dataChecksum),
        algorithm: 'sha256'
      },
      compliance: {
        auroraStandard: this.auroraStandard,
        gumasCompliant: true,
        operatorTraceability: true
      }
    };
  }

  private async verifyManifest(manifest: ExportManifest, manifestPath: string): Promise<boolean> {
    // Verify operator
    if (manifest.operatorId !== this.operatorId) {
      return false;
    }

    // Verify compliance
    if (!manifest.compliance.auroraStandard || !manifest.compliance.gumasCompliant) {
      return false;
    }

    // Verify file checksums
    const manifestDir = path.dirname(manifestPath);
    
    for (const fileInfo of manifest.files) {
      try {
        const filePath = path.join(manifestDir, fileInfo.filename);
        const fileData = await fs.promises.readFile(filePath);
        const calculatedChecksum = this.calculateChecksum(fileData);
        
        if (calculatedChecksum !== fileInfo.checksum) {
          return false;
        }
      } catch {
        return false;
      }
    }

    return true;
  }

  private calculateChecksum(data: Buffer): string {
    return crypto.createHash('sha256').update(data).digest('hex');
  }

  private generateSignature(checksum: string): string {
    return crypto.createHash('sha256').update(checksum + this.operatorId + this.auroraStandard).digest('hex');
  }

  private generateEncryptionKey(): string {
    return crypto.randomBytes(32).toString('hex');
  }

  private generateExportId(): string {
    return `export_${Date.now()}_${this.operatorId}`;
  }

  private generateFilename(exportId: string, format: ExportFormat): string {
    return `${exportId}.${format}`;
  }

  private async ensureDirectory(dirPath: string): Promise<void> {
    try {
      await fs.promises.access(dirPath);
    } catch {
      await fs.promises.mkdir(dirPath, { recursive: true });
    }
  }

  private toYaml(obj: any, indent: number = 0): string {
    // Simple YAML serialization - replace with proper library in production
    const spaces = '  '.repeat(indent);
    
    if (typeof obj === 'string') {
      return `"${obj}"`;
    } else if (typeof obj === 'number' || typeof obj === 'boolean') {
      return String(obj);
    } else if (Array.isArray(obj)) {
      return obj.map(item => `${spaces}- ${this.toYaml(item, indent + 1)}`).join('\n');
    } else if (typeof obj === 'object' && obj !== null) {
      return Object.entries(obj)
        .map(([key, value]) => `${spaces}${key}: ${this.toYaml(value, indent + 1)}`)
        .join('\n');
    }
    
    return 'null';
  }

  private parseYaml(yamlString: string): any {
    // Simple YAML parsing - replace with proper library in production
    try {
      // For now, just try to parse as JSON if it's JSON-like
      return JSON.parse(yamlString);
    } catch {
      throw new Error('YAML parsing not implemented - use JSON format');
    }
  }

  private parseBinary(data: Buffer): any {
    // Simple binary parsing - just treat as JSON for now
    return JSON.parse(data.toString('utf8'));
  }
}