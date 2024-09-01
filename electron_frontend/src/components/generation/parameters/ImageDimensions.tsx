import { Dispatch, SetStateAction } from 'react';
import { Form, Slider, InputNumber, Row, Col } from 'antd';

interface ImageDimensionsProps {
  width: number;
  height: number;
  setWidth: Dispatch<SetStateAction<number>>;
  setHeight: Dispatch<SetStateAction<number>>;
}

const ImageDimensions = ({ width, height, setWidth, setHeight }: ImageDimensionsProps) => {
  return (
    <div className="p-6">
      <p className="text-[14px] font-semibold text-[#222] mb-3">Image Dimensions</p>
      <Form layout="vertical" className="space-y-4">
        <Form.Item label="Width">
          <Row gutter={16}>
            <Col span={16}>
              <Slider
                min={128}
                max={2048}
                value={width}
                onChange={(value) => setWidth(value as number)}
                tooltip={{ open: undefined }}
              />
            </Col>
            <Col span={8}>
              <InputNumber
                min={128}
                max={2048}
                value={width}
                onChange={(value) => setWidth(value ?? 128)}
                className="w-full"
              />
            </Col>
          </Row>
        </Form.Item>

        <Form.Item label="Height">
          <Row gutter={16}>
            <Col span={16}>
              <Slider
                min={128}
                max={2048}
                value={height}
                onChange={(value) => setHeight(value as number)}
                tooltip={{ open: undefined }}
              />
            </Col>
            <Col span={8}>
              <InputNumber
                min={128}
                max={2048}
                value={height}
                onChange={(value) => setHeight(value ?? 128)}
                className="w-full"
              />
            </Col>
          </Row>
        </Form.Item>
      </Form>
    </div>
  );
};

export default ImageDimensions;
