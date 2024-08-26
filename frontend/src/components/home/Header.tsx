const Header = () => {
  return (
    <div className="relative overflow-hidden w-full h-[535px] sm:h-[600px] md:h-[700px] lg:h-[800px]">
      <div className="absolute inset-0">
        <img src={'../public/homeimg.png'} className="w-full h-full object-cover" />
      </div>
      <div className="absolute inset-x-0 top-[-24px] w-full h-[862px]">
        <img src="레이어-1-1.png" className="w-full h-full object-cover" />
      </div>
      <p className="absolute text-white font-bold text-left px-4 md:px-12 lg:px-24 xl:px-32 text-[24px] sm:text-[30px] md:text-[36px] lg:text-[40px] top-[20%] sm:top-[25%] md:top-[30%]">
        Imagine, Create, and Innovate with Defect Studio
      </p>
      <div className="absolute left-1/2 transform -translate-x-1/2 top-[55%] sm:top-[60%] md:top-[65%] w-11/12 sm:w-9/12 md:w-8/12 lg:w-7/12 xl:w-[750px] h-14 sm:h-16">
        <div className="bg-white rounded-[20px] w-full h-full" />
        <div className="absolute right-0 top-2 sm:top-3 w-[100px] sm:w-[134px] h-8 sm:h-10">
          <div className="bg-blue-700 rounded-full w-full h-full" />
          <div className="absolute top-1.5 left-4 sm:left-5 text-white font-bold flex items-center">
            <img src="sparkling.png" className="w-4 h-4 sm:w-[18px] sm:h-[18px] mr-2" />
            <p className="text-sm sm:text-base">Generate</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;
