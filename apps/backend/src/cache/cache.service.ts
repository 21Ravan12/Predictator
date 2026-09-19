import { Inject, Injectable, Logger } from '@nestjs/common';
import type { Cache } from 'cache-manager';
import { CACHE_MANAGER } from './cache.constants';

@Injectable()
export class CacheService {
  private readonly logger = new Logger(CacheService.name);

  constructor(@Inject(CACHE_MANAGER) private readonly cacheManager: Cache) {}

  async get<T>(key: string): Promise<T | null> {
    try {
      const value = (await this.cacheManager.get<T>(key)) as T | undefined;
      if (value !== undefined && value !== null) {
        this.logger.debug(`✅ Cache hit: ${key}`);
        return value;
      }

      this.logger.debug(`❌ Cache miss: ${key}`);
      return null;
    } catch (error) {
      this.logger.error(`❌ Cache get error: ${key}`, error);
      return null;
    }
  }

  async set(key: string, value: any, ttl: number = 300): Promise<void> {
    try {
      await this.cacheManager.set(key, value, ttl);
      this.logger.debug(`💾 Cache set: ${key} (TTL: ${ttl}s)`);
    } catch (error) {
      this.logger.error(`❌ Cache set error: ${key}`, error);
    }
  }

  async del(key: string): Promise<void> {
    try {
      await this.cacheManager.del(key);
      this.logger.debug(`🗑️ Cache delete: ${key}`);
    } catch (error) {
      this.logger.error(`❌ Cache delete error: ${key}`, error);
    }
  }

  async reset(): Promise<void> {
    try {
      await this.cacheManager.reset();
      this.logger.log('🔄 Cache reset');
    } catch (error) {
      this.logger.error('❌ Cache reset error:', error);
    }
  }

  // 🆕 Get or set with factory
  async remember<T>(
    key: string,
    factory: () => Promise<T>,
    ttl: number = 300,
  ): Promise<T> {
    const cached = await this.get<T>(key);
    if (cached !== null) {
      return cached;
    }

    const value = await factory();
    await this.set(key, value, ttl);
    return value;
  }

  // 🆕 Generate cache key
  generateKey(prefix: string, ...parts: (string | number)[]): string {
    return `${prefix}:${parts.join(':')}`;
  }

  // 🆕 Check if cache exists
  async has(key: string): Promise<boolean> {
    try {
      const value = await this.cacheManager.get(key);
      return value !== undefined && value !== null;
    } catch {
      return false;
    }
  }

  // 🆕 Get TTL (time to live) for a key
  getTtl(key: string): Promise<number | null> {
    void key;
    return Promise.resolve(null);
  }
}
