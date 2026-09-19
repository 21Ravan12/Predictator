import { Module, Global } from '@nestjs/common';
import { PredictorClient } from './predictor.client';
import { PredictorController } from './predictor.controller';

@Global()
@Module({
  providers: [PredictorClient],
  controllers: [PredictorController],
  exports: [PredictorClient],
})
export class PredictorModule {}
