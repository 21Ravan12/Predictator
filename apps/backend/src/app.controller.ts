import { Controller, Get, HttpCode, HttpStatus } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';

@ApiTags('App')
@Controller()
export class AppController {
  @Get()
  @ApiOperation({ summary: 'Root endpoint' })
  @ApiResponse({ status: 200, description: 'API is running' })
  getHello(): string {
    return '🚀 Predictator API is running!';
  }

  @Get('health')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Health check endpoint' })
  @ApiResponse({ status: 200, description: 'Service health status' })
  health(): {
    status: string;
    service: string;
    version: string;
    timestamp: string;
    environment: string;
  } {
    return {
      status: 'healthy',
      service: 'predictator-backend',
      version: '2.0.0',
      timestamp: new Date().toISOString(),
      environment: process.env.NODE_ENV || 'development',
    };
  }

  @Get('ping')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Simple ping endpoint' })
  ping(): { ping: string; timestamp: string } {
    return {
      ping: 'pong',
      timestamp: new Date().toISOString(),
    };
  }
}
