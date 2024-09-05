import axios, { AxiosResponse } from "axios";

type departmentType = {
  department_id: number;
  department_name: string;
};

export const getAllDepartments = async () => {
  try {
    const response = await axios.get<departmentType[]>(
      "http://j11s001.p.ssafy.io:8000/api/departments"
    );
    console.log(response);
    return response;
  } catch (error) {
    throw new Error("Failed to get all departments");
  }
};
