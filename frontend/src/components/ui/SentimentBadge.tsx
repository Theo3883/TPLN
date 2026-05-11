interface SentimentBadgeProps {
  label: 'pozitiv' | 'negativ' | 'neutru';
  score?: number;
  confidence?: number;
  showDetails?: boolean;
}

export function SentimentBadge({ 
  label, 
  score, 
  confidence, 
  showDetails = false 
}: SentimentBadgeProps) {
  const getEmoji = (label: string) => {
    switch (label) {
      case 'pozitiv': return '😊';
      case 'negativ': return '😢';
      case 'neutru': return '😐';
      default: return '😐';
    }
  };
  
  const getBgColor = (label: string) => {
    switch (label) {
      case 'pozitiv': return 'bg-green-100 text-green-700 border-green-200';
      case 'negativ': return 'bg-red-100 text-red-700 border-red-200';
      case 'neutru': return 'bg-gray-100 text-gray-700 border-gray-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };
  
  return (
    <span 
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-medium border ${getBgColor(label)}`}
      title={showDetails && score !== undefined ? `Score: ${(score * 100).toFixed(0)}%, Confidence: ${((confidence || 0) * 100).toFixed(0)}%` : undefined}
    >
      <span className="text-base leading-none">{getEmoji(label)}</span>
      <span className="capitalize">{label}</span>
      {showDetails && score !== undefined && (
        <span className="text-xs opacity-75 ml-0.5">
          ({(score * 100).toFixed(0)}%)
        </span>
      )}
    </span>
  );
}
