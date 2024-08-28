// const WordSuggestionModal = ({ isModalOpen, setIsModalOpen, suggestedWords, setPrompt }) => (
//   <>
//     {isModalOpen && (
//       <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
//         <div className="bg-[#2a2a45] p-6 rounded-md max-w-md w-full mx-4">
//           <h2 className="text-[#e0e0e0] text-[18px] font-black mb-4">AI 이미지 생성 단어</h2>
//           <div className="grid grid-cols-2 gap-2">
//             {suggestedWords.map((word) => (
//               <button
//                 key={word}
//                 onClick={() => setPrompt((prev) => `${prev} ${word}`)}
//                 className="py-2 px-4 bg-[#121224] text-[#e0e0e0] rounded-md hover:bg-[#3a3a5a] transition"
//               >
//                 {word}
//               </button>
//             ))}
//           </div>
//           <button
//             onClick={() => setIsModalOpen(false)}
//             className="mt-4 py-2 px-4 bg-[#f0a500] text-[#121224] text-[14px] font-black rounded-lg hover:bg-[#e09400] transition"
//           >
//             닫기
//           </button>
//         </div>
//       </div>
//     )}
//   </>
// );

// export default WordSuggestionModal;
