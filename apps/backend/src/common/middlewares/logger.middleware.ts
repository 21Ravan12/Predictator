import { Injectable, NestMiddleware, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';

@Injectable()
export class LoggerMiddleware implements NestMiddleware {
  private readonly logger = new Logger('HTTP');

  use(req: Request, res: Response, next: NextFunction): void {
    const { method, originalUrl, ip, headers } = req;
    const userAgent = headers['user-agent'] || 'unknown';
    const startTime = Date.now();

    // Log request
    this.logger.log(`🌐 ${method} ${originalUrl} - ${ip} - ${userAgent}`);

    // Track response
    res.on('finish', () => {
      const { statusCode } = res;
      const duration = Date.now() - startTime;
      const statusColor =
        statusCode >= 400 ? '❌' : statusCode >= 300 ? '⚠️' : '✅';

      this.logger.log(
        `${statusColor} ${method} ${originalUrl} - ${statusCode} - ${duration}ms`,
      );
    });

    next();
  }
}
