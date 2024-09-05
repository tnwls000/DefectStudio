import { useNavigate } from "react-router-dom";

const MiniProfileLogin = () => {
  const navigate = useNavigate();
  return (
    <>
      <div className="w-[300px] h-[150px] relative">
        <div
          className="w-[300px] h-[150px] absolute left-[-1px] top-[-1px] rounded-[10px] bg-white border border-[#e0e0e0]"
          style={{ boxShadow: "0px 4px 4px 0 rgba(0,0,0,0.25)" }}
        />
        <p className="absolute left-[114px] top-[10px] text-base text-left text-black">
          Log in for Generation AI!
        </p>
        <div className="w-[94px] h-[37px] absolute left-[38px] top-[100px]">
          <button
            onClick={() => {
              navigate("/login");
            }}
            className="btn w-[94px] h-[37px] absolute left-[-1px] top-[-1px] rounded-[10px] text-base bg-[#fd7272] hover:bg-[#f26a6a] text-white active:scale-95"
          >
            Go to Login
          </button>
        </div>
      </div>
      ;
    </>
  );
};

export default MiniProfileLogin;
