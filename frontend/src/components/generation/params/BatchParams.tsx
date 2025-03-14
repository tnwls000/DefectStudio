import { InputNumber, Form, Row, Col } from 'antd';
import React from 'react';
import { BatchParamsType } from '../../../types/generation';

interface BatchParamsProps {
  batchParams: BatchParamsType;
  updateBatchParams: (batchCount: number, batchSize: number) => void;
}

const BatchParams = ({ batchParams, updateBatchParams }: BatchParamsProps) => {
  const { batchCount, batchSize } = batchParams;

  const handleBatchChange = (key: 'batchCount' | 'batchSize', value: number | null) => {
    if (value !== null) {
      const newBatchCount = key === 'batchCount' ? value : batchCount;
      const newBatchSize = key === 'batchSize' ? value : batchSize;
      updateBatchParams(newBatchCount, newBatchSize);
    }
  };

  return (
    <div className="px-6 pt-6 pb-10">
      <p className="text-[14px] font-semibold text-[#222] mb-3 dark:text-gray-300">Batch Settings</p>
      <Form layout="vertical" className="space-y-4">
        <div className="flex justify-between gap-6">
          <Row gutter={16}>
            {/* Batch count */}
            <Col span={12}>
              <Form.Item label="Batch count" className="mb-0">
                <InputNumber
                  value={batchCount}
                  onChange={(value) => handleBatchChange('batchCount', value)}
                  className="w-full"
                  min={1}
                />
              </Form.Item>
            </Col>

            {/* Batch size */}
            <Col span={12}>
              <Form.Item label="Batch size" className="mb-0">
                <InputNumber
                  value={batchSize}
                  onChange={(value) => handleBatchChange('batchSize', value)}
                  className="w-full"
                  min={1}
                />
              </Form.Item>
            </Col>
          </Row>
        </div>
      </Form>
    </div>
  );
};

export default React.memo(BatchParams);
