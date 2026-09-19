import { Module, Global } from '@nestjs/common';
import { createCache, memoryStore } from 'cache-manager';
import { CacheService } from './cache.service';
import { CACHE_MANAGER } from './cache.constants';

@Global()
@Module({
  providers: [
    {
      provide: CACHE_MANAGER,
      useFactory: () => createCache(memoryStore({ max: 100, ttl: 300 * 1000 })),
    },
    CacheService,
  ],
  exports: [CACHE_MANAGER, CacheService],
})
export class CacheModule {}
