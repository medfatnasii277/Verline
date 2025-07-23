import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Star, User, Eye, Calendar, Palette, MessageCircle, ArrowLeft } from "lucide-react";
import { api, Painting, Comment, Rating } from "@/services/api";
import { useAuth } from "@/contexts/AuthContext";
import { Header } from "@/components/Header";
import { StarRating } from "@/components/StarRating";
import { useToast } from "@/hooks/use-toast";

const PaintingDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [newComment, setNewComment] = useState("");
  const [userRating, setUserRating] = useState<number>(0);

  // Get painting details
  const { data: painting, isLoading: paintingLoading } = useQuery<Painting>({
    queryKey: ["painting", id],
    queryFn: () => api.paintings.getById(parseInt(id!)),
    enabled: !!id,
  });

  // Get painting comments
  const { data: comments, isLoading: commentsLoading } = useQuery<Comment[]>({
    queryKey: ["comments", id],
    queryFn: () => api.comments.getPaintingComments(parseInt(id!)),
    enabled: !!id,
  });

  // Get user's rating for this painting
  const { data: ratings } = useQuery<Rating[]>({
    queryKey: ["ratings", id, user?.id],
    queryFn: () => api.ratings.getPaintingRatings(parseInt(id!)),
    enabled: !!id && !!user,
  });

  // Set user's current rating
  useEffect(() => {
    if (ratings && user) {
      const userRatingObj = ratings.find(r => r.user_id === user.id);
      if (userRatingObj) {
        setUserRating(userRatingObj.rating);
      }
    }
  }, [ratings, user]);

  // Add comment mutation
  const addCommentMutation = useMutation({
    mutationFn: (content: string) => {
      if (!user) {
        throw new Error('User not authenticated');
      }
      console.log('Current user object:', user);
      console.log('Adding comment:', { paintingId: parseInt(id!), userId: user.id, content });
      console.log('Auth token:', localStorage.getItem('access_token'));
      return api.comments.create(parseInt(id!), user.id, content);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["comments", id] });
      setNewComment("");
      toast({
        title: "Success",
        description: "Comment added successfully",
      });
    },
    onError: (error) => {
      console.error('Comment creation error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to add comment';
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    },
  });

  // Add/update rating mutation
  const addRatingMutation = useMutation({
    mutationFn: (rating: number) => 
      api.ratings.create(parseInt(id!), rating),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ratings", id, user?.id] });
      toast({
        title: "Success",
        description: "Rating submitted successfully",
      });
    },
    onError: (error) => {
      console.error('Rating creation error:', error);
      toast({
        title: "Error",
        description: "Failed to submit rating",
        variant: "destructive",
      });
    },
  });

  const handleAddComment = () => {
    if (!user) {
      toast({
        title: "Authentication Required",
        description: "Please log in to add comments",
        variant: "destructive",
      });
      return;
    }
    
    if (!painting) {
      toast({
        title: "Error",
        description: "Painting not found",
        variant: "destructive",
      });
      return;
    }
    
    if (newComment.trim()) {
      addCommentMutation.mutate(newComment.trim());
    }
  };

  const handleRating = (rating: number) => {
    if (!user) {
      toast({
        title: "Authentication Required",
        description: "Please log in to rate paintings",
        variant: "destructive",
      });
      return;
    }
    setUserRating(rating);
    addRatingMutation.mutate(rating);
  };

  if (paintingLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="text-lg">Loading painting...</div>
          </div>
        </div>
      </div>
    );
  }

  if (!painting) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">
        <Header />
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="text-lg text-red-600">Painting not found</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50">
      <Header />
      
      <div className="container mx-auto px-4 py-8">
        {/* Back button */}
        <Button
          variant="ghost"
          onClick={() => navigate(-1)}
          className="mb-6 flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Gallery
        </Button>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main painting details */}
          <div className="lg:col-span-2">
            <Card className="overflow-hidden">
              <div className="aspect-video relative">
                <img
                  src={painting.image_url}
                  alt={painting.title}
                  className="w-full h-full object-cover"
                />
              </div>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-2xl">{painting.title}</CardTitle>
                    <p className="text-muted-foreground mt-1">
                      by {painting.artist?.full_name}
                    </p>
                  </div>
                  <Badge variant="secondary" className="flex items-center gap-1">
                    <Palette className="h-3 w-3" />
                    {painting.category?.name}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 mb-6">{painting.description}</p>
                
                {/* Painting metadata */}
                <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    Created: {new Date(painting.created_at).toLocaleDateString()}
                  </div>
                  <div className="flex items-center gap-1">
                    <Eye className="h-4 w-4" />
                    Views: {painting.view_count || 0}
                  </div>
                  {painting.average_rating && painting.rating_count > 0 && (
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      {painting.average_rating.toFixed(1)} ({painting.rating_count} ratings)
                    </div>
                  )}
                </div>

                {/* Rating system */}
                {user && (
                  <div className="mt-6 pt-6 border-t">
                    <h3 className="text-lg font-semibold mb-3">Rate this painting</h3>
                    <StarRating
                      currentRating={userRating}
                      onRate={handleRating}
                      disabled={addRatingMutation.isPending}
                    />
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Artist info */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Artist Information
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3 mb-4">
                  <Avatar>
                    <AvatarFallback>
                      {painting.artist?.full_name?.[0]}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <div className="font-medium">
                      {painting.artist?.full_name}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      @{painting.artist?.username}
                    </div>
                  </div>
                </div>
                {painting.artist?.bio && (
                  <p className="text-sm text-gray-600">{painting.artist.bio}</p>
                )}
              </CardContent>
            </Card>

            {/* Comments section */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageCircle className="h-5 w-5" />
                  Comments ({comments?.length || 0})
                </CardTitle>
              </CardHeader>
              <CardContent>
                {/* Add comment form */}
                {user && (
                  <div className="space-y-3 mb-6">
                    <Textarea
                      placeholder="Add a comment..."
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      className="resize-none"
                    />
                    <Button
                      onClick={handleAddComment}
                      disabled={!newComment.trim() || addCommentMutation.isPending}
                      className="w-full"
                    >
                      {addCommentMutation.isPending ? "Adding..." : "Add Comment"}
                    </Button>
                  </div>
                )}

                {/* Comments list */}
                <div className="space-y-4">
                  {commentsLoading ? (
                    <div className="text-center text-muted-foreground">
                      Loading comments...
                    </div>
                  ) : comments && comments.length > 0 ? (
                    comments.map((comment) => (
                      <div key={comment.id} className="border-b pb-3 last:border-b-0">
                        <div className="flex items-start gap-3">
                          <Avatar className="h-8 w-8">
                            <AvatarFallback className="text-xs">
                              {comment.user?.full_name?.[0]}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-sm font-medium">
                                {comment.user?.full_name}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                {new Date(comment.created_at).toLocaleDateString()}
                              </span>
                            </div>
                            <p className="text-sm text-gray-700">{comment.content}</p>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center text-muted-foreground">
                      No comments yet. Be the first to comment!
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PaintingDetail;
