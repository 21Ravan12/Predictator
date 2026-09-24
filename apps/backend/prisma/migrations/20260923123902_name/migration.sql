-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "firstName" TEXT NOT NULL,
    "lastName" TEXT NOT NULL,
    "roles" TEXT[] DEFAULT ARRAY['user']::TEXT[],
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sessions" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "expiresAt" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "sessions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "predictions" (
    "id" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "category" TEXT DEFAULT 'Electronics',
    "date" TIMESTAMP(3) NOT NULL,
    "sales" DOUBLE PRECISION NOT NULL,
    "confidenceLower" DOUBLE PRECISION,
    "confidenceUpper" DOUBLE PRECISION,
    "alert" TEXT,
    "floorLimit" INTEGER DEFAULT 0,
    "dictatorApplied" BOOLEAN NOT NULL DEFAULT false,
    "alertTriggered" BOOLEAN NOT NULL DEFAULT false,
    "userId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "predictions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "categories" (
    "id" TEXT NOT NULL,
    "categoryId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "icon" TEXT,
    "seasonalityFactor" DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    "holidaySensitivity" DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "categories_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "products" (
    "id" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "categoryId" TEXT,
    "categoryName" TEXT,
    "brand" TEXT,
    "unitPrice" DOUBLE PRECISION,
    "costPrice" DOUBLE PRECISION,
    "minStock" INTEGER NOT NULL DEFAULT 0,
    "maxStock" INTEGER NOT NULL DEFAULT 1000,
    "reorderPoint" INTEGER NOT NULL DEFAULT 50,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "seasonalityFactor" DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    "holidaySensitivity" DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    "avgDailySales" DOUBLE PRECISION,
    "avgWeeklySales" DOUBLE PRECISION,
    "avgMonthlySales" DOUBLE PRECISION,
    "description" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "products_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sales_history" (
    "id" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,
    "sales" DOUBLE PRECISION NOT NULL,
    "price" DOUBLE PRECISION,
    "category" TEXT,
    "holidayName" TEXT,
    "seasonName" TEXT,
    "eventType" TEXT DEFAULT 'Normal',
    "temperature" DOUBLE PRECISION,
    "weatherCondition" TEXT,
    "humidity" DOUBLE PRECISION,
    "windSpeed" DOUBLE PRECISION,
    "promotion" BOOLEAN NOT NULL DEFAULT false,
    "discountPercent" DOUBLE PRECISION,
    "promotionType" TEXT,
    "stockLevel" INTEGER,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "sales_history_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "holiday_bank" (
    "id" TEXT NOT NULL,
    "holidayName" TEXT NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,
    "preImpactDays" INTEGER NOT NULL DEFAULT 3,
    "postImpactDays" INTEGER NOT NULL DEFAULT 2,
    "impactStrength" INTEGER NOT NULL DEFAULT 5,
    "affectedCategories" TEXT,
    "description" TEXT,
    "region" TEXT NOT NULL DEFAULT 'Baku',
    "isRecurring" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "holiday_bank_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "season_bank" (
    "id" TEXT NOT NULL,
    "seasonName" TEXT NOT NULL,
    "startDate" TIMESTAMP(3) NOT NULL,
    "endDate" TIMESTAMP(3) NOT NULL,
    "region" TEXT NOT NULL DEFAULT 'Baku',
    "impactCategory" TEXT,
    "impactStrength" INTEGER NOT NULL DEFAULT 5,
    "preImpactDays" INTEGER NOT NULL DEFAULT 3,
    "postImpactDays" INTEGER NOT NULL DEFAULT 3,
    "affectedCategories" TEXT,
    "description" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "season_bank_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "alerts" (
    "id" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "category" TEXT,
    "level" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "message" TEXT NOT NULL,
    "holidayName" TEXT,
    "seasonName" TEXT,
    "eventType" TEXT,
    "data" JSONB,
    "read" BOOLEAN NOT NULL DEFAULT false,
    "resolved" BOOLEAN NOT NULL DEFAULT false,
    "resolvedAt" TIMESTAMP(3),
    "userId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "alerts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "training_logs" (
    "id" TEXT NOT NULL,
    "trainingDate" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "samplesUsed" INTEGER NOT NULL,
    "modelType" TEXT NOT NULL DEFAULT 'xgboost',
    "nEstimators" INTEGER,
    "maxDepth" INTEGER,
    "learningRate" DOUBLE PRECISION,
    "featureCount" INTEGER,
    "r2Score" DOUBLE PRECISION,
    "mae" DOUBLE PRECISION,
    "rmse" DOUBLE PRECISION,
    "mape" DOUBLE PRECISION,
    "productIdsTrained" TEXT,
    "categoriesTrained" TEXT,
    "dateRangeStart" TIMESTAMP(3),
    "dateRangeEnd" TIMESTAMP(3),
    "trainingDurationMs" DOUBLE PRECISION,
    "success" BOOLEAN NOT NULL DEFAULT true,
    "errorMessage" TEXT,
    "featureImportanceJson" JSONB,

    CONSTRAINT "training_logs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "feature_store" (
    "id" TEXT NOT NULL,
    "productId" TEXT NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,
    "category" TEXT,
    "featureVersion" TEXT NOT NULL DEFAULT 'v1',
    "featureCount" INTEGER,
    "featuresJson" JSONB NOT NULL,
    "lag1" DOUBLE PRECISION,
    "lag7" DOUBLE PRECISION,
    "lag28" DOUBLE PRECISION,
    "rollingMean7" DOUBLE PRECISION,
    "rollingMean30" DOUBLE PRECISION,
    "trend" DOUBLE PRECISION,
    "seasonal" DOUBLE PRECISION,
    "holidayIntensity" DOUBLE PRECISION,
    "seasonIntensity" DOUBLE PRECISION,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "feature_store_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "sessions_token_key" ON "sessions"("token");

-- CreateIndex
CREATE INDEX "predictions_productId_idx" ON "predictions"("productId");

-- CreateIndex
CREATE INDEX "predictions_date_idx" ON "predictions"("date");

-- CreateIndex
CREATE INDEX "predictions_userId_idx" ON "predictions"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "categories_categoryId_key" ON "categories"("categoryId");

-- CreateIndex
CREATE UNIQUE INDEX "products_productId_key" ON "products"("productId");

-- CreateIndex
CREATE INDEX "products_categoryName_idx" ON "products"("categoryName");

-- CreateIndex
CREATE INDEX "sales_history_productId_idx" ON "sales_history"("productId");

-- CreateIndex
CREATE INDEX "sales_history_date_idx" ON "sales_history"("date");

-- CreateIndex
CREATE INDEX "sales_history_category_idx" ON "sales_history"("category");

-- CreateIndex
CREATE INDEX "holiday_bank_holidayName_idx" ON "holiday_bank"("holidayName");

-- CreateIndex
CREATE INDEX "holiday_bank_date_idx" ON "holiday_bank"("date");

-- CreateIndex
CREATE INDEX "season_bank_seasonName_idx" ON "season_bank"("seasonName");

-- CreateIndex
CREATE INDEX "season_bank_startDate_idx" ON "season_bank"("startDate");

-- CreateIndex
CREATE INDEX "season_bank_endDate_idx" ON "season_bank"("endDate");

-- CreateIndex
CREATE INDEX "alerts_productId_idx" ON "alerts"("productId");

-- CreateIndex
CREATE INDEX "alerts_level_idx" ON "alerts"("level");

-- CreateIndex
CREATE INDEX "alerts_createdAt_idx" ON "alerts"("createdAt");

-- CreateIndex
CREATE INDEX "training_logs_trainingDate_idx" ON "training_logs"("trainingDate");

-- CreateIndex
CREATE INDEX "feature_store_productId_date_idx" ON "feature_store"("productId", "date");

-- CreateIndex
CREATE INDEX "feature_store_featureVersion_idx" ON "feature_store"("featureVersion");

-- AddForeignKey
ALTER TABLE "sessions" ADD CONSTRAINT "sessions_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "predictions" ADD CONSTRAINT "predictions_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "products" ADD CONSTRAINT "products_categoryId_fkey" FOREIGN KEY ("categoryId") REFERENCES "categories"("categoryId") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sales_history" ADD CONSTRAINT "sales_history_productId_fkey" FOREIGN KEY ("productId") REFERENCES "products"("productId") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "alerts" ADD CONSTRAINT "alerts_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE SET NULL ON UPDATE CASCADE;
