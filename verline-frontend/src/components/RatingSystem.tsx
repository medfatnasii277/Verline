import { useState } from "react";
import { Star } from "lucide-react";
import { Button } from "@/components/ui/button";

interface RatingSystemProps {
  currentRating?: number;
  onRate: (rating: number) => void;
  disabled?: boolean;
}

import { useState } from "react";
import { Star } from "lucide-react";
import { Button } from "@/components/ui/button";

interface RatingSystemProps {
  currentRating?: number;
  onRate: (rating: number) => void;
  disabled?: boolean;
}

export const RatingSystem = ({ currentRating, onRate, disabled = false }: RatingSystemProps) => {
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

export const RatingSystem = ({ artworkId, userRole, canRate = true }: RatingSystemProps) => {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [comment, setComment] = useState("");
  const [showCommentForm, setShowCommentForm] = useState(false);

  // Placeholder data
  const artworkRating = {
    average: 4.6,
    total: 124,
    distribution: [
      { stars: 5, count: 78 },
      { stars: 4, count: 32 },
      { stars: 3, count: 10 },
      { stars: 2, count: 3 },
      { stars: 1, count: 1 }
    ]
  };

  const comments = [
    {
      id: "1",
      user: "Emily Rodriguez",
      avatar: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face",
      rating: 5,
      comment: "Absolutely stunning work! The use of color and texture creates such an emotional impact.",
      time: "2 days ago",
      likes: 12
    },
    {
      id: "2", 
      user: "Michael Chen",
      avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face",
      rating: 4,
      comment: "Beautiful composition. The artist's technique really shines through in this piece.",
      time: "1 week ago",
      likes: 8
    }
  ];

  const handleRating = (value: number) => {
    if (canRate && userRole === 'enthusiast') {
      setRating(value);
      // Here you would typically send the rating to your backend
    }
  };

  const handleSubmitComment = () => {
    if (comment.trim()) {
      // Here you would typically send the comment to your backend
      setComment("");
      setShowCommentForm(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Rating Overview */}
      <Card className="bg-card border-border shadow-subtle">
        <CardHeader>
          <CardTitle className="text-lg font-light">Ratings & Reviews</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Overall Rating */}
          <div className="flex items-center gap-6">
            <div className="text-center">
              <div className="text-4xl font-light text-foreground">{artworkRating.average}</div>
              <div className="flex items-center justify-center mb-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`h-4 w-4 ${
                      star <= Math.round(artworkRating.average)
                        ? 'fill-yellow-500 text-yellow-500'
                        : 'text-muted-foreground'
                    }`}
                  />
                ))}
              </div>
              <div className="text-sm text-muted-foreground">
                {artworkRating.total} reviews
              </div>
            </div>

            {/* Rating Distribution */}
            <div className="flex-1 space-y-2">
              {artworkRating.distribution.map((dist) => (
                <div key={dist.stars} className="flex items-center gap-3">
                  <span className="text-sm text-muted-foreground w-8">
                    {dist.stars}★
                  </span>
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-yellow-500 rounded-full transition-all"
                      style={{ 
                        width: `${(dist.count / artworkRating.total) * 100}%` 
                      }}
                    />
                  </div>
                  <span className="text-sm text-muted-foreground w-8">
                    {dist.count}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* User Rating */}
          {userRole === 'enthusiast' && canRate && (
            <div className="border-t border-border pt-6">
              <h4 className="text-sm font-medium mb-3">Rate this artwork:</h4>
              <div className="flex items-center gap-1 mb-4">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`h-6 w-6 cursor-pointer transition-colors ${
                      star <= (hoverRating || rating)
                        ? 'fill-yellow-500 text-yellow-500'
                        : 'text-muted-foreground hover:text-yellow-400'
                    }`}
                    onMouseEnter={() => setHoverRating(star)}
                    onMouseLeave={() => setHoverRating(0)}
                    onClick={() => handleRating(star)}
                  />
                ))}
              </div>
              {rating > 0 && (
                <p className="text-sm text-muted-foreground">
                  Thank you for rating this artwork!
                </p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Comments Section */}
      <Card className="bg-card border-border shadow-subtle">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg font-light">Comments</CardTitle>
          {userRole && (
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setShowCommentForm(!showCommentForm)}
            >
              <MessageCircle className="h-4 w-4 mr-2" />
              Add Comment
            </Button>
          )}
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Comment Form */}
          {showCommentForm && userRole && (
            <div className="border border-border rounded-lg p-4 bg-gallery">
              <Textarea
                placeholder="Share your thoughts about this artwork..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className="mb-3 bg-background border-border"
              />
              <div className="flex gap-2 justify-end">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setShowCommentForm(false)}
                >
                  Cancel
                </Button>
                <Button 
                  size="sm"
                  onClick={handleSubmitComment}
                  disabled={!comment.trim()}
                  className="bg-artwork text-artwork-foreground hover:bg-artwork/90"
                >
                  Post Comment
                </Button>
              </div>
            </div>
          )}

          {/* Comments List */}
          <div className="space-y-4">
            {comments.map((comment) => (
              <div key={comment.id} className="flex gap-3 p-4 bg-gallery rounded-lg">
                <Avatar className="w-10 h-10">
                  <AvatarImage src={comment.avatar} alt={comment.user} />
                  <AvatarFallback>
                    {comment.user.split(' ').map(n => n[0]).join('')}
                  </AvatarFallback>
                </Avatar>
                
                <div className="flex-1 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gallery-foreground">
                        {comment.user}
                      </span>
                      <div className="flex items-center">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <Star
                            key={star}
                            className={`h-3 w-3 ${
                              star <= comment.rating
                                ? 'fill-yellow-500 text-yellow-500'
                                : 'text-muted-foreground'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {comment.time}
                    </span>
                  </div>
                  
                  <p className="text-gallery-foreground leading-relaxed">
                    {comment.comment}
                  </p>
                  
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <button className="flex items-center gap-1 hover:text-foreground transition-colors">
                      <Heart className="h-3 w-3" />
                      {comment.likes}
                    </button>
                    <button className="flex items-center gap-1 hover:text-foreground transition-colors">
                      <MessageCircle className="h-3 w-3" />
                      Reply
                    </button>
                    <button className="flex items-center gap-1 hover:text-destructive transition-colors">
                      <Flag className="h-3 w-3" />
                      Report
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Load More Comments */}
          <div className="text-center">
            <Button variant="outline" size="sm">
              Load More Comments
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};