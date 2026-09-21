import { ApiProperty } from '@nestjs/swagger';
import {
  IsString,
  IsInt,
  IsOptional,
  Min,
  Max,
  IsNotEmpty,
  MinLength,
} from 'class-validator';
import { Expose, Transform } from 'class-transformer';

export class PredictDto {
  @ApiProperty({
    example: 'P001',
    description: 'Product ID to predict sales for',
    minLength: 2,
  })
  @Expose({ name: 'product_id' })
  @Transform(({ value, obj }) => value ?? obj?.product_id ?? obj?.productId)
  @IsString()
  @IsNotEmpty()
  @MinLength(2)
  productId!: string;

  @ApiProperty({
    example: 7,
    description: 'Number of days to predict ahead',
    minimum: 1,
    maximum: 30,
    default: 7,
  })
  @Expose({ name: 'days_ahead' })
  @Transform(({ value, obj }) => value ?? obj?.days_ahead ?? obj?.daysAhead)
  @IsInt()
  @Min(1)
  @Max(30)
  daysAhead!: number;

  @ApiProperty({
    example: 0,
    description: 'Minimum sales floor limit (0 = disabled)',
    required: false,
    default: 0,
  })
  @Expose({ name: 'floor_limit' })
  @Transform(({ value, obj }) => value ?? obj?.floor_limit ?? obj?.floorLimit)
  @IsInt()
  @Min(0)
  @IsOptional()
  floorLimit?: number;
}
