'use client';

import { useState } from 'react';

interface ConstraintEditorProps {
  productId?: string;
  onSave?: (constraints: unknown) => void;
}

export default function ConstraintEditor({ productId = 'P001', onSave }: ConstraintEditorProps) {
  const [floorLimit, setFloorLimit] = useState(150);
  const [stockLimit, setStockLimit] = useState(500);
  const [isActive, setIsActive] = useState(true);

  const handleSave = () => {
    const constraints = {
      product_id: productId,
      floor_limit: floorLimit,
      stock_limit: stockLimit,
      is_active: isActive,
    };
    onSave?.(constraints);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
      <h3 className="font-semibold text-gray-800 mb-3">👑 Dictator Rules — {productId}</h3>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <label className="text-sm text-gray-600">Floor Limit</label>
          <input
            type="number"
            value={floorLimit}
            onChange={(e) => setFloorLimit(Number(e.target.value))}
            className="w-24 px-3 py-1 border border-gray-300 rounded-lg text-sm"
          />
        </div>

        <div className="flex items-center justify-between">
          <label className="text-sm text-gray-600">Stock Limit</label>
          <input
            type="number"
            value={stockLimit}
            onChange={(e) => setStockLimit(Number(e.target.value))}
            className="w-24 px-3 py-1 border border-gray-300 rounded-lg text-sm"
          />
        </div>

        <div className="flex items-center justify-between">
          <label className="text-sm text-gray-600">Active</label>
          <button
            onClick={() => setIsActive(!isActive)}
            className={`px-3 py-1 rounded-lg text-sm transition ${
              isActive ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'
            }`}
          >
            {isActive ? '✅ Active' : '⏸️ Inactive'}
          </button>
        </div>

        <button
          onClick={handleSave}
          className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm"
        >
          💾 Save Constraints
        </button>
      </div>
    </div>
  );
}
