// apps/backend/prisma/seed.ts
import { PrismaClient } from '@prisma/client';
import * as fs from 'fs';
import * as path from 'path';

type SeedPrismaClient = PrismaClient & {
  category: {
    upsert: (...args: any[]) => Promise<unknown>;
    count: () => Promise<number>;
  };
  product: {
    upsert: (...args: any[]) => Promise<unknown>;
    count: () => Promise<number>;
  };
};

const prisma = new PrismaClient() as SeedPrismaClient;

type CategoryRow = {
  category_id: string;
  name: string;
  description?: string;
  icon?: string;
  seasonality_factor?: string;
  holiday_sensitivity?: string;
};

type ProductRow = {
  product_id: string;
  name: string;
  category_id?: string;
  category?: string;
  brand?: string;
  unit_price?: string;
  cost_price?: string;
  min_stock?: string;
  max_stock?: string;
  reorder_point?: string;
  is_active?: string;
  seasonality_factor?: string;
  holiday_sensitivity?: string;
  description?: string;
};

const toNumber = (value?: string, fallback = 0): number => {
  const parsed = Number.parseFloat(value ?? '');
  return Number.isFinite(parsed) ? parsed : fallback;
};

const toInteger = (value?: string, fallback = 0): number => {
  const parsed = Number.parseInt(value ?? '', 10);
  return Number.isFinite(parsed) ? parsed : fallback;
};

// ============================================
// 📖 CSV Parser
// ============================================
function parseCSV<T extends Record<string, string | undefined>>(
  filePath: string,
): T[] {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.trim().split('\n');
  const headers = lines[0]?.split(',').map((h) => h.trim()) ?? [];

  return lines.slice(1).flatMap((line) => {
    if (!line.trim()) {
      return [];
    }

    const values = line.split(',').map((v) => v.trim());
    const row = {} as Record<string, string | undefined>;

    headers.forEach((header, i) => {
      row[header] = values[i];
    });

    return [row as T];
  });
}

// ============================================
// 🌱 Seeder
// ============================================
async function main() {
  console.log('🌱 Starting database seed...\n');

  const dataDir = path.join(__dirname, 'data');

  // ----------------------------------------
  // 1. Seed Categories
  // ----------------------------------------
  console.log('📦 Seeding categories...');
  const categoriesData = parseCSV<CategoryRow>(
    path.join(dataDir, 'categories.csv'),
  );

  for (const cat of categoriesData) {
    const categoryId = cat.category_id;
    const seasonalityFactor = toNumber(cat.seasonality_factor, 1);
    const holidaySensitivity = toNumber(cat.holiday_sensitivity, 1);

    await prisma.category.upsert({
      where: { categoryId },
      update: {
        name: cat.name,
        description: cat.description ?? null,
        icon: cat.icon ?? null,
        seasonalityFactor,
        holidaySensitivity,
      },
      create: {
        categoryId,
        name: cat.name,
        description: cat.description ?? null,
        icon: cat.icon ?? null,
        seasonalityFactor,
        holidaySensitivity,
        isActive: true,
      },
    });
    console.log(`   ✅ ${cat.icon ?? '📦'} ${cat.name} (${categoryId})`);
  }

  // ----------------------------------------
  // 2. Seed Products
  // ----------------------------------------
  console.log('\n🛍️  Seeding products...');
  const productsData = parseCSV<ProductRow>(path.join(dataDir, 'products.csv'));

  for (const prod of productsData) {
    const productId = prod.product_id;
    const categoryConnect = prod.category_id
      ? { category: { connect: { categoryId: prod.category_id } } }
      : {};

    await prisma.product.upsert({
      where: { productId },
      update: {
        name: prod.name,
        categoryName: prod.category ?? null,
        brand: prod.brand ?? null,
        unitPrice: toNumber(prod.unit_price),
        costPrice: toNumber(prod.cost_price),
        minStock: toInteger(prod.min_stock, 0),
        maxStock: toInteger(prod.max_stock, 1000),
        reorderPoint: toInteger(prod.reorder_point, 50),
        isActive: prod.is_active === 'true',
        seasonalityFactor: toNumber(prod.seasonality_factor, 1),
        holidaySensitivity: toNumber(prod.holiday_sensitivity, 1),
        description: prod.description ?? null,
        ...categoryConnect,
      },
      create: {
        productId,
        name: prod.name,
        categoryName: prod.category ?? null,
        brand: prod.brand ?? null,
        unitPrice: toNumber(prod.unit_price),
        costPrice: toNumber(prod.cost_price),
        minStock: toInteger(prod.min_stock, 0),
        maxStock: toInteger(prod.max_stock, 1000),
        reorderPoint: toInteger(prod.reorder_point, 50),
        isActive: prod.is_active === 'true',
        seasonalityFactor: toNumber(prod.seasonality_factor, 1),
        holidaySensitivity: toNumber(prod.holiday_sensitivity, 1),
        description: prod.description ?? null,
        ...categoryConnect,
      },
    });
    console.log(`   ✅ ${productId} - ${prod.name}`);
  }

  // ----------------------------------------
  // 3. Summary
  // ----------------------------------------
  const categoryCount = await prisma.category.count();
  const productCount = await prisma.product.count();

  console.log('\n' + '='.repeat(50));
  console.log(`🎉 Seeding complete!`);
  console.log(`   📁 Categories: ${categoryCount}`);
  console.log(`   📦 Products:   ${productCount}`);
  console.log('='.repeat(50));
}

main()
  .catch((e) => {
    console.error('❌ Seed failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
