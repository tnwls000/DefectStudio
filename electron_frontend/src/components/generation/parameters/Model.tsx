import { Dispatch, SetStateAction } from "react";
import { Select, Form } from "antd";

interface ModelProps {
  model: string;
  setModel: Dispatch<SetStateAction<string>>;
}

const Model = ({ model, setModel }: ModelProps) => {
  return (
    <div className="px-6 pt-6 pb-2">
      <p className="text-[14px] font-semibold mb-3 text-[#222] dark:text-gray-300">
        Model
      </p>
      <Form layout="vertical">
        <Form.Item>
          <Select
            value={model}
            onChange={setModel}
            options={[
              {
                value: "Stable Diffusion v1-5",
                label: "Stable Diffusion v1-5",
              },
              {
                value: "Stable Diffusion v2-1",
                label: "Stable Diffusion v2-1",
              },
              { value: "Custom Model", label: "Custom Model" },
            ]}
            placeholder="Select a model"
          />
        </Form.Item>
      </Form>
    </div>
  );
};

export default Model;
