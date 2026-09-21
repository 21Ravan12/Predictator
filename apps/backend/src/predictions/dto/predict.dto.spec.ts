import { plainToInstance } from 'class-transformer';
import { validateSync } from 'class-validator';
import { describe, expect, it } from '@jest/globals';
import { PredictDto } from './predict.dto';

describe('PredictDto', () => {
  it('accepts snake_case payload fields from the frontend', () => {
    const dto = plainToInstance(PredictDto, {
      product_id: 'P001',
      days_ahead: 7,
      floor_limit: 3,
    });

    const errors = validateSync(dto);

    expect(errors).toHaveLength(0);
    expect(dto.productId).toBe('P001');
    expect(dto.daysAhead).toBe(7);
    expect(dto.floorLimit).toBe(3);
  });
});
