import { registerAs } from '@nestjs/config';

export default registerAs('grpc', () => ({
  // gRPC server configuration (for ML Engine)
  url: process.env.ML_ENGINE_GRPC_URL || 'localhost:50051',
  package: 'predictor',
  protoPath: process.env.GRPC_PROTO_PATH || 'proto/predictor.proto',

  // gRPC client options
  options: {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true,
  },

  // gRPC connection settings
  connection: {
    timeout: parseInt(process.env.GRPC_TIMEOUT as string, 10) || 30000,
    maxRetries: parseInt(process.env.GRPC_MAX_RETRIES as string, 10) || 3,
    retryDelay: parseInt(process.env.GRPC_RETRY_DELAY as string, 10) || 1000,
  },

  // gRPC health check
  healthCheck: {
    enabled: process.env.GRPC_HEALTH_CHECK !== 'false',
    interval: parseInt(process.env.GRPC_HEALTH_INTERVAL as string, 10) || 30000, // 30 seconds
  },

  // gRPC service names
  services: {
    predictor: 'PredictorService',
  },

  // gRPC methods
  methods: {
    getPrediction: 'GetPrediction',
    getPredictionsStream: 'GetPredictionsStream',
    trainModel: 'TrainModel',
    getTrainingStatus: 'GetTrainingStatus',
  },
}));
