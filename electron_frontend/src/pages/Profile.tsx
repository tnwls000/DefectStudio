interface ProfileProps {
  name: string;
  nickname: string;
  email: string;
  role: string[];
  department: {
    name: string;
  };
  token_quantity: number;
}

const dummyProfile: ProfileProps = {
  name: "김싸피",
  nickname: "삼성에들어가고싶은김싸피",
  email: "ssafy:ssafy.com",
  role: ["삼성전자", "삼성전자 DX"],
  department: {
    name: "삼성전자 DX",
  },
  token_quantity: 12345000,
};

const Profile = () => {
  const userInfo = dummyProfile;
  return (
    <>
      <div className="w-full max-w-5xl bg-white py-10 px-12 rounded-[20px] mx-auto border border-gray-300 shadow-md h-full overflow-y-auto custom-scrollbar">
        <div className="w-[90%] max-w-[1156px] mx-auto mt-8">
          <div className="rounded-[20px] bg-white border border-[#e0e0e0] shadow-md p-6">
            <div className="flex flex-col lg:flex-row">
              <div className="flex flex-col items-center">
                <svg
                  width={141}
                  height={141}
                  viewBox="0 0 141 141"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  className="mb-4"
                  preserveAspectRatio="xMidYMid meet"
                >
                  <path
                    d="M139 70.5C139 108.332 108.332 139 70.5 139C32.6685 139 2 108.332 2 70.5C2 32.6685 32.6685 2 70.5 2C108.332 2 139 32.6685 139 70.5Z"
                    fill="#C4C4C4"
                    stroke="#8A2BE2"
                    strokeWidth={4}
                  />
                </svg>
                <p className="text-3xl text-black">Profile</p>
              </div>
              <div className="lg:ml-10 mt-8 lg:mt-0 flex-1">
                <div className="flex flex-col space-y-4">
                  <div>
                    <p className="text-xl text-black">Nickname</p>
                    <p className="text-base text-black mt-1">
                      삼성에들어가고싶은김싸피
                    </p>
                  </div>
                  <div>
                    <p className="text-xl text-black">Name</p>
                    <p className="text-base text-black mt-1">김싸피</p>
                  </div>
                  <div>
                    <p className="text-3xl text-black">Information</p>
                    <div className="border border-[#3A3A5A] rounded-md p-2 mt-2">
                      <p className="text-base text-black">Department</p>
                      <p className="text-base text-black mt-1">
                        Samsung Electronic Co. DX
                      </p>
                    </div>
                    <div className="border border-[#3A3A5A] rounded-md p-2 mt-4">
                      <p className="text-base text-black">Email</p>
                      <p className="text-base text-black mt-1">
                        ssafy@ssafy.com
                      </p>
                    </div>
                    <div className="border border-[#3A3A5A] rounded-md p-2 mt-4">
                      <p className="text-base text-black">Role</p>
                      <p className="text-base text-black mt-1">
                        Samsung Electronic Co. DX
                      </p>
                    </div>
                  </div>
                  <button className="w-[101px] h-10 bg-[#8a2be2] rounded-[10px] text-xl text-white mt-6">
                    Edit
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8">
            <p className="text-3xl text-black">Token Status</p>
            <div className="border border-[#2c2c3a] rounded-[10px] bg-white p-4 mt-2">
              <p className="text-base text-black">
                Left total tokens: 12345000
              </p>
              <p className="text-base text-black mt-2">Usage Tokens Table</p>
              <p className="text-base text-black mt-8">
                여기에는 사용량에 따른 그래프 표를 보여줌
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Profile;
