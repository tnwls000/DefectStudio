import "./SearchDepartments.css";
import { useQuery } from "@tanstack/react-query";
import { Input } from "antd";
import { useEffect, useState } from "react";
import { getAllDepartments } from "../../../api/getAllDepartment";
import { AxiosError, AxiosResponse } from "axios";
import { Table } from "antd";

type departmentType = {
  department_id: number;
  department_name: string;
};

type TableDepartmentType = {
  department_id: number;
  department_name: string;
  key: React.Key;
};

const SearchDepartments = () => {
  const [searchDepartmentName, setSearchDepartmentName] = useState("");
  const [filteredData, setFilteredData] = useState<TableDepartmentType[]>([]);
  const { data, isPending, isError, error } = useQuery<
    AxiosResponse<departmentType[]>,
    AxiosError,
    TableDepartmentType[],
    string[]
  >({
    queryKey: ["departments"],
    queryFn: getAllDepartments,
    select: (response) =>
      response.data.map((department) => {
        return {
          department_id: department.department_id,
          department_name: department.department_name,
          key: department.department_id,
        };
      }),
  });

  useEffect(() => {
    if (data) {
      setFilteredData(
        data.filter((department) =>
          department.department_name
            .toLowerCase()
            .includes(searchDepartmentName.toLowerCase())
        )
      );
    }
  }, [searchDepartmentName, data]);

  const columns = [
    {
      title: "Department ID",
      dataIndex: "department_id",
      key: "department_id",
    },
    {
      title: "Department Name",
      dataIndex: "department_name",
      key: "department_name",
    },
  ];
  return (
    <section className="token-issurance-department-container">
      <div>
        <p className="text-[20px] font-bold">
          Please select the departments you wish to grant the token to
        </p>
        <Input
          onChange={(e) => setSearchDepartmentName(e.target.value)}
          className="h-[40px] mt-2"
        />
      </div>

      <div className="">
        {isPending && <p>Loading...</p>}
        {isError && <p>{error.message}</p>}
        {data && (
          <Table columns={columns} dataSource={data} rowKey="department_id" />
        )}
      </div>
    </section>
  );
};

export default SearchDepartments;
