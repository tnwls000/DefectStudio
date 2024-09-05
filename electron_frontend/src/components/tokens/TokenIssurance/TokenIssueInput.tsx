import "./TokenIssueInput.css";
import { Input } from "antd";

const TokenIssueInput = () => {
  return (
    <div className="token-issurance-input-container">
      <p className="text-[20px] font-bold">Token Issue</p>

      <div>
        <p className="mt-4 text-[18px]">
          Specify the amount of tokens to be issued to the respective department
        </p>
        <Input className="h-[40px] mt-2" />
      </div>

      <div>
        <p className="mt-4 text-[18px]">Enter the token Expiration Date</p>
        <Input className="h-[40px] mt-2" />
      </div>
    </div>
  );
};

export default TokenIssueInput;
