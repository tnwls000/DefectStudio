const Header = () => {
  return (
    <div className="relative overflow-hidden flex items-center justify-center w-full h-[535px] bg-gray-300">
      <div className="absolute inset-0">
        <img src={'./homeimg.png'} alt="Background" className="w-full h-full object-cover z-0" />
      </div>
      <div className="relative text-center text-white p-4">
        <p className="text-2xl md:text-4xl font-bold mb-8">Imagine, Create, and Innovate with Defect Studio</p>
        <div className="relative w-full max-w-[750px] mx-auto">
          <div className="bg-white rounded-[20px] h-16 flex items-center justify-center w-full">
            <div className="relative flex justify-end items-center w-full h-full pr-5">
              <div className="bg-blue-700 rounded-full w-[134px] h-10 flex items-center justify-center absolute right-4">
                <img src={'./src/assets/sparkling.png'} alt="Sparkling" className="w-4 h-4 mr-2" />
                <p className="text-white font-bold">Generate</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;
