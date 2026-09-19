import { Injectable, OnModuleInit, Logger } from '@nestjs/common';
import {
  ClientGrpc,
  ClientOptions,
  ClientProxyFactory,
  Transport,
} from '@nestjs/microservices';
import { join } from 'path';
import { Observable } from 'rxjs';
import { Metadata } from '@grpc/grpc-js';
import { ConfigService } from '@nestjs/config';

// Types for gRPC communication
export interface PredictionRequest {
  product_id: string;
  days_ahead: number;
  floor_limit: number;
}

export interface PredictionResponse {
  success: boolean;
  product_id: string;
  predictions: Prediction[];
  summary: Summary;
  dictator_actions: DictatorAction[];
}

export interface Prediction {
  date: string;
  predicted_sales: number;
  confidence_lower: number;
  confidence_upper: number;
  alert: string;
}

export interface Summary {
  total_predicted: number;
  average_daily: number;
  peak_day: number;
  floor_violations: number;
}

export interface DictatorAction {
  day: number;
  message: string;
}

export interface TrainRequest {
  csv_path: string;
  force_retrain: boolean;
}

export interface TrainResponse {
  success: boolean;
  message: string;
  samples_used: number;
  metrics: {
    r2: number;
    mae: number;
    rmse: number;
    n_features: number;
  };
}

export interface TrainingStatusResponse {
  is_trained: boolean;
  last_training_date: string;
  metrics: {
    r2: number;
    mae: number;
    rmse: number;
    n_features: number;
  };
}

interface PredictorServiceClient {
  getPrediction(
    request: PredictionRequest,
    metadata?: Metadata,
  ): Observable<PredictionResponse>;
  getPredictionsStream(
    request: PredictionRequest,
  ): Observable<PredictionResponse>;
  trainModel(request: TrainRequest): Observable<TrainResponse>;
  getTrainingStatus(request: any): Observable<TrainingStatusResponse>;
}

@Injectable()
export class PredictorClient implements OnModuleInit {
  private client: PredictorServiceClient | undefined;
  private readonly logger = new Logger(PredictorClient.name);
  private isConnected = false;
  private connectionError: string | null = null;

  constructor(private configService: ConfigService) {}

  getGrpcOptions(): ClientOptions {
    const grpcUrl =
      this.configService.get<string>('ML_ENGINE_GRPC_URL') || 'localhost:50051';

    this.logger.log(`🔗 Configuring gRPC client for ML Engine at ${grpcUrl}`);

    return {
      transport: Transport.GRPC,
      options: {
        package: 'predictor',
        protoPath: join(__dirname, '../../../proto/predictor.proto'),
        url: grpcUrl,
        loader: {
          keepCase: true,
          longs: String,
          enums: String,
          defaults: true,
          oneofs: true,
        },
      },
    };
  }

  onModuleInit() {
    this.logger.log('🔧 Initializing gRPC client...');
    try {
      const options = this.getGrpcOptions();
      // For NestJS microservices client
      const clientGrpc = this.createClient(options);
      this.client =
        clientGrpc.getService<PredictorServiceClient>('PredictorService');
      this.isConnected = true;
      this.logger.log('✅ gRPC client initialized successfully');
    } catch (error) {
      this.isConnected = false;
      this.connectionError =
        error instanceof Error ? error.message : String(error);
      this.logger.error(
        `❌ Failed to initialize gRPC client: ${this.connectionError}`,
      );
    }
  }

  private createClient(options: ClientOptions): ClientGrpc {
    return ClientProxyFactory.create(options) as unknown as ClientGrpc;
  }

  private getClient(): PredictorServiceClient {
    if (!this.isConnected || !this.client) {
      throw new Error(
        `gRPC client not connected: ${this.connectionError || 'Unknown error'}`,
      );
    }

    return this.client;
  }

  async getPrediction(request: PredictionRequest): Promise<PredictionResponse> {
    this.logger.log(
      `📊 Predicting for ${request.product_id}, ${request.days_ahead} days`,
    );

    const client = this.getClient();

    return new Promise((resolve, reject) => {
      client.getPrediction(request).subscribe({
        next: (response) => {
          this.logger.log(`✅ Prediction received for ${request.product_id}`);
          resolve(response);
        },
        error: (err: unknown) => {
          const error = err instanceof Error ? err : new Error(String(err));
          this.logger.error(`❌ gRPC prediction error: ${error.message}`);
          reject(error);
        },
      });
    });
  }

  async trainModel(request: TrainRequest): Promise<TrainResponse> {
    this.logger.log('🧠 Training model requested...');

    const client = this.getClient();

    return new Promise((resolve, reject) => {
      client.trainModel(request).subscribe({
        next: (response) => {
          this.logger.log(`✅ Training complete: ${response.message}`);
          resolve(response);
        },
        error: (err: unknown) => {
          const error = err instanceof Error ? err : new Error(String(err));
          this.logger.error(`❌ gRPC training error: ${error.message}`);
          reject(error);
        },
      });
    });
  }

  async getTrainingStatus(): Promise<TrainingStatusResponse> {
    this.logger.log('📊 Getting training status...');

    const client = this.getClient();

    return new Promise((resolve, reject) => {
      client.getTrainingStatus({}).subscribe({
        next: (response) => {
          resolve(response);
        },
        error: (err: unknown) => {
          const error = err instanceof Error ? err : new Error(String(err));
          this.logger.error(`❌ gRPC status error: ${error.message}`);
          reject(error);
        },
      });
    });
  }

  getConnectionStatus(): { connected: boolean; error: string | null } {
    return {
      connected: this.isConnected,
      error: this.connectionError,
    };
  }
}
