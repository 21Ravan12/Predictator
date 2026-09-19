import { Injectable, Inject, Logger } from '@nestjs/common';
import type { Cache } from 'cache-manager';
import { CACHE_MANAGER } from '../cache/cache.constants';
import {
  PredictorClient,
  PredictionResponse,
  TrainResponse,
  TrainingStatusResponse,
} from '../grpc/predictor.client';

@Injectable()
export class PredictionsService {
  private readonly logger = new Logger(PredictionsService.name);

  constructor(
    private predictorClient: PredictorClient,
    @Inject(CACHE_MANAGER) private readonly cacheManager: Cache,
  ) {}

  async generatePredictions(
    productId: string,
    daysAhead: number,
    floorLimit: number = 0,
  ): Promise<PredictionResponse> {
    this.logger.log(`🔍 Generating predictions for ${productId}`);

    // Check cache
    const cacheKey = `predictions_${productId}_${daysAhead}_${floorLimit}`;
    const cached = await this.cacheManager.get<PredictionResponse>(cacheKey);
    if (cached) {
      this.logger.log('📦 Returning cached predictions');
      return cached;
    }

    // Call ML Engine via gRPC
    try {
      const result = await this.predictorClient.getPrediction({
        product_id: productId,
        days_ahead: daysAhead,
        floor_limit: floorLimit,
      });

      // Cache result (5 minutes)
      await this.cacheManager.set(cacheKey, result, 300);
      this.logger.log('💾 Predictions cached');

      return result;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error(`❌ gRPC call failed: ${message}`);
      throw new Error(`ML Engine error: ${message}`);
    }
  }

  async retrainModel(
    csvPath?: string,
    forceRetrain: boolean = true,
  ): Promise<TrainResponse> {
    this.logger.log('🔄 Retraining model requested');
    try {
      const result = await this.predictorClient.trainModel({
        csv_path: csvPath || '',
        force_retrain: forceRetrain,
      });

      // Clear cache after retraining
      await this.cacheManager.reset();
      this.logger.log('🗑️ Cache cleared after retraining');

      return result;
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error(`❌ Training failed: ${message}`);
      throw new Error(`Training error: ${message}`);
    }
  }

  async getTrainingStatus(): Promise<TrainingStatusResponse> {
    try {
      return await this.predictorClient.getTrainingStatus();
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error(`❌ Status check failed: ${message}`);
      throw new Error(`Status check error: ${message}`);
    }
  }

  getProducts() {
    // This would call the ML Engine to get available products
    // For now, return a default list
    return {
      products: ['P001', 'P002', 'P003'],
      categories: ['Electronics', 'Food', 'Clothing'],
    };
  }
}
