import { Injectable, Logger } from '@nestjs/common';
import { DatabaseService } from '../database/database.service';
import { PredictorClient } from '../grpc/predictor.client';
import { CacheService } from '../cache/cache.service';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class HealthService {
  private readonly logger = new Logger(HealthService.name);

  constructor(
    private databaseService: DatabaseService,
    private predictorClient: PredictorClient,
    private cacheService: CacheService,
    private configService: ConfigService,
  ) {}

  async checkAll() {
    const checks = {
      database: await this.checkDatabase(),
      grpc: await this.checkGrpc(),
      cache: await this.checkCache(),
      environment: this.checkEnvironment(),
    };

    const allHealthy = Object.values(checks).every(
      (check) => check.status === 'healthy',
    );

    return {
      status: allHealthy ? 'healthy' : 'unhealthy',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '2.0.0',
      checks: {
        ...checks,
        uptime: this.getUptime(),
      },
    };
  }

  liveness() {
    return {
      status: 'alive',
      timestamp: new Date().toISOString(),
    };
  }

  async readiness() {
    const checks = {
      database: await this.checkDatabase(),
      grpc: await this.checkGrpc(),
      cache: await this.checkCache(),
    };

    const allReady = Object.values(checks).every(
      (check) => check.status === 'healthy',
    );

    return {
      status: allReady ? 'ready' : 'not-ready',
      timestamp: new Date().toISOString(),
      checks,
    };
  }

  async checkDatabase() {
    try {
      const healthy = await this.databaseService.isHealthy();
      return {
        status: healthy ? 'healthy' : 'unhealthy',
        message: healthy ? 'Database connected' : 'Database connection failed',
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: error instanceof Error ? error.message : String(error),
      };
    }
  }

  async checkGrpc() {
    try {
      // Try to get training status as a health check
      const status = await this.predictorClient.getTrainingStatus();
      return {
        status: status ? 'healthy' : 'unhealthy',
        message: 'gRPC service is responsive',
        details: {
          isTrained: status?.is_trained || false,
        },
      };
    } catch (error) {
      this.logger.error('gRPC health check failed:', error);
      return {
        status: 'unhealthy',
        message: error instanceof Error ? error.message : String(error),
      };
    }
  }

  async checkCache() {
    try {
      const testKey = 'health:test';
      await this.cacheService.set(testKey, 'test', 1);
      const value = await this.cacheService.get(testKey);
      await this.cacheService.del(testKey);

      return {
        status: value === 'test' ? 'healthy' : 'unhealthy',
        message: value === 'test' ? 'Cache working' : 'Cache read failed',
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: error instanceof Error ? error.message : String(error),
      };
    }
  }

  checkEnvironment() {
    const env = this.configService.get<string>('NODE_ENV') ?? 'development';
    const port = this.configService.get<number>('PORT') ?? 4000;
    const grpcUrl =
      this.configService.get<string>('ML_ENGINE_GRPC_URL') ?? 'localhost:50051';

    return {
      status: 'healthy',
      message: `Environment: ${env}`,
      details: {
        environment: env,
        port,
        grpcUrl,
      },
    };
  }

  async grpcHealth() {
    try {
      const status = await this.predictorClient.getTrainingStatus();
      return {
        status: 'healthy',
        message: 'gRPC connection established',
        model: {
          isTrained: status?.is_trained || false,
          r2: status?.metrics?.r2 || 0,
        },
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: error instanceof Error ? error.message : String(error),
      };
    }
  }

  getUptime() {
    const uptimeSeconds = process.uptime();
    const hours = Math.floor(uptimeSeconds / 3600);
    const minutes = Math.floor((uptimeSeconds % 3600) / 60);
    const seconds = Math.floor(uptimeSeconds % 60);
    return {
      seconds: Math.floor(uptimeSeconds),
      formatted: `${hours}h ${minutes}m ${seconds}s`,
    };
  }
}
