import { useState } from "react";
import { Star } from "lucide-react";
import { Button } from "@/components/ui/button";

interface StarRatingProps {
  currentRating?: number;
  onRate: (rating: number) => void;
  disabled?: boolean;
}

export const StarRating = ({ currentRating, onRate, disabled = false }: StarRatingProps) => {
  const [hoverRating, setHoverRating] = useState(0);

  const handleClick = (rating: number) => {
    if (disabled) return;
    onRate(rating);
  };

  const getStarColor = (starIndex: number) => {
    const ratingToCheck = hoverRating || currentRating || 0;
    return starIndex <= ratingToCheck ? "text-yellow-500 fill-current" : "text-muted-foreground";
  };

  return (
    <div className="flex items-center space-x-1">
      {[1, 2, 3, 4, 5].map((starIndex) => (
        <Button
          key={starIndex}
          variant="ghost"
          size="sm"
          className="p-1 h-auto"
          disabled={disabled}
          onClick={() => handleClick(starIndex)}
          onMouseEnter={() => !disabled && setHoverRating(starIndex)}
          onMouseLeave={() => !disabled && setHoverRating(0)}
        >
          <Star 
            className={`h-5 w-5 ${getStarColor(starIndex)} transition-colors`}
          />
        </Button>
      ))}
      
      {currentRating && (
        <span className="ml-2 text-sm text-muted-foreground">
          Your rating: {currentRating}/5
        </span>
      )}
    </div>
  );
};
