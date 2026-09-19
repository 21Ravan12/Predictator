import { Injectable, Logger } from '@nestjs/common';

interface LogRequest {
  method?: string;
  url?: string;
  ip?: string;
  headers: Record<string, string | string[] | undefined>;
}

@Injectable()
export class LoggingService {
  private readonly logger = new Logger(LoggingService.name);

  // 📊 Log levels
  debug(message: string, context?: string): void {
    Logger.debug(message, context ?? LoggingService.name);
  }

  info(message: string, context?: string): void {
    Logger.log(message, context ?? LoggingService.name);
  }

  warn(message: string, context?: string): void {
    Logger.warn(message, context ?? LoggingService.name);
  }

  error(message: string, trace?: string, context?: string): void {
    Logger.error(message, trace, context ?? LoggingService.name);
  }

  verbose(message: string, context?: string): void {
    Logger.verbose(message, context ?? LoggingService.name);
  }

  // 🆕 Structured logging
  logRequest(request: LogRequest): void {
    const { method, url, ip, headers } = request;
    const userAgentHeader = headers['user-agent'];
    const userAgent = Array.isArray(userAgentHeader)
      ? userAgentHeader.join(', ')
      : (userAgentHeader ?? 'unknown');
    this.info(`📥 ${method} ${url} - ${ip} - ${userAgent}`);
  }

  logResponse(request: LogRequest, statusCode: number, duration: number): void {
    const { method, url } = request;
    const emoji = statusCode >= 400 ? '❌' : statusCode >= 300 ? '⚠️' : '✅';
    this.info(`${emoji} ${method} ${url} - ${statusCode} - ${duration}ms`);
  }

  // 🆕 Log performance
  logPerformance(operation: string, duration: number): void {
    this.info(`⏱️ ${operation} - ${duration}ms`);
  }

  // 🆕 Log with metadata
  logWithMeta(message: string, meta: Record<string, unknown>): void {
    this.info(`${message} ${JSON.stringify(meta)}`);
  }
}
