import "./TokenIssueInput.css";
import { DatePicker, InputNumber } from "antd";
import dayjs from "dayjs";

const disabledDate = (current: dayjs.Dayjs) => {
  // 과거 날짜는 선택할 수 없도록 함 (오늘 포함)
  return current && current < dayjs().startOf("day");
};

const TokenIssueInput = () => {
  return (
    <div className="token-issurance-input-container">
      <p className="title">Token Issue</p>

      <div>
        <p className="sub-title">
          Specify the amount of tokens to be issued to the respective department
        </p>
        <InputNumber className="input-number-container" />
      </div>

      <div>
        <p className="sub-title">Enter the token Expiration Date</p>
        <DatePicker
          className="input-number-container"
          defaultValue={dayjs(new Date())}
          disabledDate={disabledDate}
        />
      </div>
    </div>
  );
};

export default TokenIssueInput;
