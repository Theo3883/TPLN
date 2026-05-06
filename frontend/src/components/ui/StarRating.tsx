import React from 'react';
import { Star, StarHalf } from 'lucide-react';
import { cn } from '../../lib/utils';

interface StarRatingProps {
  rating: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  interactive?: boolean;
  onChange?: (rating: number) => void;
  className?: string;
}

export default function StarRating({ 
  rating, 
  max = 5, 
  size = 'md', 
  interactive = false, 
  onChange,
  className
}: StarRatingProps) {
  const [hoverRating, setHoverRating] = React.useState<number | null>(null);

  const starSize = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-6 h-6'
  }[size];

  const stars = [];
  const currentRating = hoverRating !== null ? hoverRating : rating;

  for (let i = 1; i <= max; i++) {
    const isFull = currentRating >= i;
    const isHalf = currentRating >= i - 0.5 && currentRating < i;

    stars.push(
      <button
        key={i}
        type={interactive ? 'button' : undefined}
        disabled={!interactive}
        onClick={() => interactive && onChange?.(i)}
        onMouseEnter={() => interactive && setHoverRating(i)}
        onMouseLeave={() => interactive && setHoverRating(null)}
        className={cn(
          "transition-all duration-200",
          interactive ? "hover:scale-110 active:scale-95 cursor-pointer" : "cursor-default"
        )}
      >
        {isHalf ? (
          <StarHalf className={cn(starSize, "fill-amber-400 text-amber-400")} />
        ) : (
          <Star 
            className={cn(
              starSize, 
              isFull ? "fill-amber-400 text-amber-400" : "text-gray-300"
            )} 
          />
        )}
      </button>
    );
  }

  return (
    <div className={cn("flex items-center gap-0.5", className)}>
      <div className="flex items-center">
        {stars}
      </div>
      {!interactive && (
        <span className={cn(
          "font-mono text-amber-800 ml-2 font-medium",
          size === 'sm' ? "text-[10px]" : "text-sm"
        )}>
          {rating.toFixed(1)}
        </span>
      )}
    </div>
  );
}
