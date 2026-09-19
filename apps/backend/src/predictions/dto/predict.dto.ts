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

export class PredictDto {
  @ApiProperty({
    example: 'P001',
    description: 'Product ID to predict sales for',
    minLength: 2,
  })
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
  @IsInt()
  @Min(0)
  @IsOptional()
  floorLimit?: number;
}
