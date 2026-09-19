import { Controller, Get, HttpCode, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { HealthService } from './health.service';

@ApiTags('Health')
@Controller('health')
export class HealthController {
  constructor(private healthService: HealthService) {}

  @Get()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Full health check' })
  @ApiResponse({ status: 200, description: 'All systems healthy' })
  @ApiResponse({ status: 503, description: 'Service unhealthy' })
  async check() {
    const status = await this.healthService.checkAll();
    return status;
  }

  @Get('liveness')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Liveness probe' })
  @ApiResponse({ status: 200, description: 'Service is alive' })
  liveness() {
    return this.healthService.liveness();
  }

  @Get('readiness')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Readiness probe' })
  @ApiResponse({ status: 200, description: 'Service is ready' })
  @ApiResponse({ status: 503, description: 'Service is not ready' })
  async readiness() {
    const status = await this.healthService.readiness();
    return status;
  }

  @Get('gprc')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'gRPC health check' })
  @ApiResponse({ status: 200, description: 'gRPC service is healthy' })
  async grpcHealth() {
    return this.healthService.grpcHealth();
  }
}
