import "./TokenTabs.css";

interface TabItem {
  id: string;
  name: string;
  value: number | string;
  onChange?: React.Dispatch<React.SetStateAction<string | number>>;
}

const tabItems: TabItem[] = [
  { id: "TokenIssurance", name: "Token Issurance", value: 1 },
  { id: "TokenDistribution", name: "Token Distribution", value: 2 },
  { id: "TokenStatistics", name: "Token Statistics", value: 3 },
];

const TokenTabs = ({ activeTab }: { activeTab: string }) => {
  return (
    <div className="mb-4 border-gray-200 dark:border-gray-700">
      <ul
        className="flex flex-wrap -mb-px text-sm font-medium text-center"
        id="default-tab"
      >
        {tabItems.map((item) => (
          <li key={item.id}>
            <button
              className={`token-tab-default ${
                activeTab === item.id
                  ? "token-tab-active"
                  : "token-tab-inactive"
              } `}
            >
              {item.name}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TokenTabs;
