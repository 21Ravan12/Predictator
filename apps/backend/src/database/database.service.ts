import {
  Injectable,
  OnModuleInit,
  OnModuleDestroy,
  Logger,
} from '@nestjs/common';
import { PrismaClient, Prisma } from '@prisma/client';

type PaginationArgs = {
  where?: Record<string, unknown>;
  [key: string]: unknown;
};

type PaginatedModel<T, TArgs extends PaginationArgs> = {
  findMany: (args: TArgs & { skip: number; take: number }) => Promise<T[]>;
  count: (args: { where?: TArgs['where'] }) => Promise<number>;
};

@Injectable()
export class DatabaseService
  extends PrismaClient
  implements OnModuleInit, OnModuleDestroy
{
  private readonly logger = new Logger(DatabaseService.name);

  constructor() {
    super({
      log:
        process.env.NODE_ENV === 'development'
          ? ['query', 'info', 'warn', 'error']
          : ['error'],
    });
  }

  async onModuleInit() {
    await this.$connect();
    this.logger.log('✅ Database connected successfully');
  }

  async onModuleDestroy() {
    await this.$disconnect();
    this.logger.log('🔌 Database disconnected');
  }

  async createUser(data: Prisma.UserCreateInput) {
    return this.user.create({ data });
  }

  async findAllUsers() {
    return this.user.findMany();
  }

  findUserById(id: string) {
    return this.user.findUnique({ where: { id } });
  }

  async findUserByEmail(email: string) {
    return this.user.findUnique({ where: { email } });
  }

  async updateUser(id: string, data: Prisma.UserUpdateInput) {
    return this.user.update({ where: { id }, data });
  }

  async deleteUser(id: string): Promise<boolean> {
    try {
      await this.user.delete({ where: { id } });
      return true;
    } catch {
      return false;
    }
  }

  // Health check method
  async isHealthy(): Promise<boolean> {
    try {
      await this.$queryRaw`SELECT 1`;
      return true;
    } catch (error) {
      this.logger.error('❌ Database health check failed:', error);
      return false;
    }
  }

  // 🆕 Transaction helper
  async transaction<T>(
    callback: (prisma: PrismaClient) => Promise<T>,
  ): Promise<T> {
    const runInTransaction = this.$transaction.bind(this) as <TResult>(
      handler: (prisma: PrismaClient) => Promise<TResult>,
    ) => Promise<TResult>;

    return runInTransaction(async (tx) => callback(tx));
  }

  // 🆕 Pagination helper
  async paginate<T, TArgs extends PaginationArgs>(
    model: PaginatedModel<T, TArgs>,
    args: TArgs,
    page = 1,
    limit = 10,
  ): Promise<{ data: T[]; total: number; page: number; totalPages: number }> {
    const skip = (page - 1) * limit;
    const [data, total] = await Promise.all([
      model.findMany({ ...args, skip, take: limit }),
      model.count({ where: args.where }),
    ]);

    return {
      data,
      total,
      page,
      totalPages: Math.ceil(total / limit),
    };
  }
}
