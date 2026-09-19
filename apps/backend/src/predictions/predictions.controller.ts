import {
  Controller,
  Post,
  Body,
  Get,
  HttpException,
  HttpStatus,
  Logger,
} from '@nestjs/common';
import { PredictionsService } from './predictions.service';
import { PredictDto } from './dto/predict.dto';
import { Public } from '../common/decorators/public.decorator';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';

@ApiTags('Predictions')
@Controller('predictions')
export class PredictionsController {
  private readonly logger = new Logger(PredictionsController.name);

  constructor(private predictionsService: PredictionsService) {}

  private getErrorMessage(error: unknown, fallback: string): string {
    return error instanceof Error ? error.message : fallback;
  }

  @Public()
  @Post()
  @ApiOperation({ summary: 'Generate sales predictions' })
  @ApiResponse({
    status: 200,
    description: 'Predictions generated successfully',
  })
  @ApiResponse({ status: 400, description: 'Invalid request' })
  @ApiResponse({ status: 500, description: 'Internal server error' })
  async generatePredictions(@Body() body: PredictDto) {
    try {
      this.logger.log(
        `📊 Generating predictions for ${body.productId}, ${body.daysAhead} days`,
      );
      const result = await this.predictionsService.generatePredictions(
        body.productId,
        body.daysAhead,
        body.floorLimit || 0,
      );

      return {
        success: true,
        product_id: body.productId,
        predictions: result.predictions,
        summary: result.summary,
        dictator_actions: result.dictator_actions,
      };
    } catch (error: unknown) {
      const message = this.getErrorMessage(
        error,
        'Failed to generate predictions',
      );
      this.logger.error(`❌ Prediction failed: ${message}`);
      throw new HttpException(message, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Post('train')
  @ApiOperation({ summary: 'Retrain the ML model' })
  @ApiResponse({ status: 200, description: 'Model retrained successfully' })
  async trainModel(@Body() body: { csvPath?: string; forceRetrain?: boolean }) {
    try {
      this.logger.log('🧠 Retraining model requested');
      const result = await this.predictionsService.retrainModel(
        body.csvPath,
        body.forceRetrain || true,
      );
      return result;
    } catch (error: unknown) {
      const message = this.getErrorMessage(error, 'Failed to train model');
      this.logger.error(`❌ Training failed: ${message}`);
      throw new HttpException(message, HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Get('status')
  @ApiOperation({ summary: 'Get training status' })
  @ApiResponse({ status: 200, description: 'Training status retrieved' })
  async getTrainingStatus() {
    try {
      return await this.predictionsService.getTrainingStatus();
    } catch (error: unknown) {
      throw new HttpException(
        this.getErrorMessage(error, 'Failed to get training status'),
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Get('products')
  @ApiOperation({ summary: 'Get all products in database' })
  @ApiResponse({ status: 200, description: 'Products retrieved' })
  getProducts() {
    try {
      return this.predictionsService.getProducts();
    } catch (error: unknown) {
      throw new HttpException(
        this.getErrorMessage(error, 'Failed to get products'),
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }

  @Get('health')
  @ApiOperation({ summary: 'Predictions module health check' })
  health() {
    return {
      status: 'healthy',
      module: 'predictions',
      timestamp: new Date().toISOString(),
    };
  }
}
