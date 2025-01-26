// components/RealTimeButton.tsx
"use client";

interface RealTimeButtonProps {
  visible: boolean;
  onClick: () => void;
}

const RealTimeButton = ({ visible, onClick }: RealTimeButtonProps) => {
  if (!visible) return null;

  return (
    <div
      className="absolute bottom-10 right-20 p-2 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition-colors z-10"
      onClick={onClick}
      style={{
        boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
      }}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 14 14"
        width={14}
        height={14}
        className="text-white"
      >
        <path
          fill="none"
          stroke="currentColor"
          strokeLinecap="round"
          strokeWidth={2}
          d="M6.5 1.5l5 5.5-5 5.5M3 4l2.5 3L3 10"
        />
      </svg>
    </div>
  );
};

export default RealTimeButton;
