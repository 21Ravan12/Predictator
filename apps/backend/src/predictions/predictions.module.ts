import { Module } from '@nestjs/common';
import { PredictionsController } from './predictions.controller';
import { PredictionsService } from './predictions.service';
import { PredictorModule } from '../grpc/predictor.module';
import { DatabaseModule } from '../database/database.module';

@Module({
  imports: [PredictorModule, DatabaseModule],
  controllers: [PredictionsController],
  providers: [PredictionsService],
  exports: [PredictionsService],
})
export class PredictionsModule {}
