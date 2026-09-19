import { Module, MiddlewareConsumer } from '@nestjs/common';
import { AppController } from './app.controller';
import { PredictorModule } from './grpc/predictor.module';
import { PredictionsModule } from './predictions/predictions.module';
import { AuthModule } from './auth/auth.module';
import { UsersModule } from './users/users.module';
import { DatabaseModule } from './database/database.module';
import { CacheModule as AppCacheModule } from './cache/cache.module';
import { LoggingModule } from './logging/logging.module';
import { HealthModule } from './health/health.module';
import { LoggerMiddleware } from './common/middlewares/logger.middleware';
import { ConfigModule } from '@nestjs/config';
import configuration from './config/configuration';
import grpcConfig from './config/grpc.config';

@Module({
  imports: [
    // ⚙️ Configuration
    ConfigModule.forRoot({
      isGlobal: true,
      load: [configuration, grpcConfig],
    }),

    // 💾 Cache (in-memory, can be swapped with Redis)
    AppCacheModule,

    // 📦 Feature Modules
    AuthModule,
    UsersModule,
    PredictorModule,
    PredictionsModule,
    DatabaseModule,
    LoggingModule,
    HealthModule,
  ],
  controllers: [AppController],
  providers: [],
})
export class AppModule {
  configure(consumer: MiddlewareConsumer) {
    consumer.apply(LoggerMiddleware).forRoutes('*');
  }
}
