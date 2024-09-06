import "./SearchDepartments.css";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { getAllDepartments } from "../../../api/getAllDepartment";
import { AxiosError, AxiosResponse } from "axios";
import { Select, Space } from "antd";

type departmentType = {
  department_id: number;
  department_name: string;
};

type AntdSelectOptionType = {
  value: number;
  label: string;
};

const SearchDepartments = () => {
  //부서 불러오기
  const {
    data = [],
    isPending,
    isError,
    error,
  } = useQuery<
    AxiosResponse<departmentType[]>,
    AxiosError,
    AntdSelectOptionType[],
    string[]
  >({
    queryKey: ["departments"],
    queryFn: getAllDepartments,
    select: (response) =>
      response.data.map((department) => {
        return {
          value: department.department_id,
          label: department.department_name,
          key: department.department_id,
        };
      }),
  });

  const [selectedItems, setSelectedItems] = useState<number[]>([]);
  const filteredOptions = data.filter(
    (item) => !selectedItems.includes(item.value)
  );
  //컴포넌트 출력
  return (
    <section className="token-issurance-department-container">
      <div>
        <p className="text-[20px] font-bold">
          Please select the departments you wish to grant the token to
        </p>
      </div>

      <div className="">
        {isPending && <p>Loading...</p>}
        {isError && <p>{error.message}</p>}
        {data && (
          <Select
            mode="multiple"
            value={selectedItems}
            onChange={setSelectedItems}
            style={{ width: "100%" }}
            options={filteredOptions.map((item) => ({
              value: item.value,
              label: item.label,
            }))}
            optionRender={(option) => <Space>{option.data.label}</Space>}
          />
        )}
      </div>
    </section>
  );
};

export default SearchDepartments;
