export default () => ({
  // Server configuration
  port: parseInt(process.env.PORT as string, 10) || 4000,
  nodeEnv: process.env.NODE_ENV || 'development',

  // CORS configuration
  cors: {
    origin: process.env.CORS_ORIGIN?.split(',') || [
      'http://localhost:3000',
      'http://localhost:3001',
      'http://localhost:5173',
    ],
    credentials: true,
  },

  // Database configuration (PostgreSQL / SQLite)
  database: {
    type: process.env.DB_TYPE || 'sqlite',
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT as string, 10) || 5432,
    username: process.env.DB_USERNAME || 'postgres',
    password: process.env.DB_PASSWORD || 'password',
    database: process.env.DB_DATABASE || 'predictator',
    url: process.env.DATABASE_URL || 'sqlite:./predictator.db',
    synchronize: process.env.DB_SYNCHRONIZE === 'true',
    logging: process.env.DB_LOGGING === 'true',
  },

  // JWT configuration
  jwt: {
    secret:
      process.env.JWT_SECRET || 'super-secret-key-change-me-in-production',
    expiresIn: process.env.JWT_EXPIRES_IN || '7d',
  },

  // Redis/Cache configuration
  cache: {
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT as string, 10) || 6379,
    password: process.env.REDIS_PASSWORD || '',
    ttl: parseInt(process.env.CACHE_TTL as string, 10) || 300, // 5 minutes
    max: parseInt(process.env.CACHE_MAX as string, 10) || 100,
  },

  // ML Engine configuration
  mlEngine: {
    grpcUrl: process.env.ML_ENGINE_GRPC_URL || 'localhost:50051',
    timeout: parseInt(process.env.ML_ENGINE_TIMEOUT as string, 10) || 30000, // 30 seconds
    maxRetries: parseInt(process.env.ML_ENGINE_MAX_RETRIES as string, 10) || 3,
  },

  // Logging configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    pretty: process.env.LOG_PRETTY === 'true',
  },

  // Rate limiting
  rateLimit: {
    ttl: parseInt(process.env.RATE_LIMIT_TTL as string, 10) || 60, // 1 minute
    limit: parseInt(process.env.RATE_LIMIT_LIMIT as string, 10) || 100, // 100 requests
  },

  // Feature flags
  features: {
    enableAuth: process.env.ENABLE_AUTH !== 'false',
    enableCache: process.env.ENABLE_CACHE !== 'false',
    enableLogging: process.env.ENABLE_LOGGING !== 'false',
    enableMetrics: process.env.ENABLE_METRICS === 'true',
  },

  // Swagger/API Documentation
  swagger: {
    enabled: process.env.SWAGGER_ENABLED !== 'false',
    title: 'Predictator API',
    description: 'Sales forecasting API with XGBoost',
    version: '2.0.0',
  },
});
