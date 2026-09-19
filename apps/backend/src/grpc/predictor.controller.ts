import { Controller, Get, Post } from '@nestjs/common';
import { PredictorClient } from './predictor.client';
import { Public } from '../common/decorators/public.decorator';

@Controller('grpc')
export class PredictorController {
  constructor(private predictorClient: PredictorClient) {}

  @Public()
  @Get('health')
  async health() {
    try {
      const status = await this.predictorClient.getTrainingStatus();
      const connection = this.predictorClient.getConnectionStatus();

      return {
        status: connection.connected ? 'healthy' : 'unhealthy',
        gRPC: connection.connected ? 'connected' : 'disconnected',
        connectionError: connection.error || null,
        mlEngine: {
          isTrained: status.is_trained,
          lastTrainingDate: status.last_training_date || null,
          metrics: status.metrics || null,
        },
        timestamp: new Date().toISOString(),
      };
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);

      console.error(message);

      return {
        status: 'unhealthy',
        gRPC: 'error',
        error: message,
        timestamp: new Date().toISOString(),
      };
    }
  }

  @Public()
  @Get('status')
  async status() {
    try {
      const status = await this.predictorClient.getTrainingStatus();
      return {
        isReady: true,
        trainingStatus: status,
        connection: this.predictorClient.getConnectionStatus(),
      };
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);

      console.error(message);

      return {
        isReady: false,
        error: message,
      };
    }
  }

  @Post('reconnect')
  reconnect() {
    // Re-initialize the gRPC client
    try {
      // Force reconnection by reinitializing
      (this.predictorClient as any).onModuleInit();
      return {
        success: true,
        message: 'gRPC client reconnected',
        connection: this.predictorClient.getConnectionStatus(),
      };
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : String(error);

      if (error instanceof Error) {
        console.error(message);
      } else {
        console.error(message);
      }
      return {
        success: false,
        error: message,
      };
    }
  }
}
