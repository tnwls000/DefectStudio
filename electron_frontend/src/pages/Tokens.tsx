import { Tabs } from "antd";
import TokenHeader from "../components/tokens/TokenHeader";
import { useState } from "react";

type TabItemType = "Issurance" | "Distribution" | "Statistics";

const TabItems = [
  {
    label: "Tab 1",
    key: "Issurance",
    children: "Tab 1",
  },
  {
    label: "Tab 2",
    key: "Distribution",
    children: "Tab 2",
  },
  {
    label: "Tab 3",
    key: "Statistics",
    children: "Tab 3",
  },
];

const Tokens = () => {
  // Tab Items
  const [activeTab, setActiveTab] = useState<string>("");

  return (
    <div className="flex justify-center items-center h-[calc(100vh-60px)] bg-gray-100 p-4 overflow-hidden dark:bg-gray-800">
      <div className="w-full max-w-5xl bg-white py-10 px-12 rounded-[20px] mx-auto border border-gray-300 shadow-md h-full overflow-y-auto custom-scrollbar dark:bg-gray-600 dark:border-none">
        <TokenHeader />
        <hr className="border-[#E6E6E6] dark:border-gray-700" />

        {activeTab !== "" && (
          <Tabs
            defaultActiveKey="1"
            items={TabItems}
            onChange={(key) => setActiveTab(key)}
          />
        )}
      </div>
    </div>
  );
};

export default Tokens;
