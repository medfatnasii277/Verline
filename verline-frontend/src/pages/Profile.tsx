import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  User, 
  Mail, 
  Calendar, 
  MapPin, 
  Edit3, 
  Save, 
  X, 
  Star, 
  Eye, 
  MessageSquare,
  Palette,
  Camera
} from "lucide-react";
import { api, User as UserType } from "@/services/api";
import { useAuth } from "@/contexts/AuthContext";
import { Header } from "@/components/Header";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

const Profile = () => {
  const { user, updateUser } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const [isEditing, setIsEditing] = useState(false);
  const [editedProfile, setEditedProfile] = useState({
    full_name: user?.full_name || "",
    bio: user?.bio || "",
    location: user?.location || "",
    website: user?.website || "",
  });

  // Fetch user's paintings (for artists)
  const { data: myPaintings } = useQuery({
    queryKey: ['myPaintings', user?.id],
    queryFn: () => user ? api.paintings.getMyPaintings(user.id) : Promise.resolve({ items: [], total: 0, page: 1, pages: 1 }),
    enabled: !!user,
  });

  // Fetch user's ratings (for enthusiasts)
  const { data: myRatings } = useQuery({
    queryKey: ['myRatings', user?.id],
    queryFn: () => user ? api.ratings.getByUser(user.id) : Promise.resolve({ items: [], total: 0, page: 1, pages: 1 }),
    enabled: !!user,
  });

  // Fetch user's comments
  const { data: myComments } = useQuery({
    queryKey: ['myComments', user?.id],
    queryFn: () => user ? api.comments.getByUser(user.id) : Promise.resolve({ items: [], total: 0, page: 1, pages: 1 }),
    enabled: !!user,
  });

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: (data: Partial<UserType>) => api.users.update(user!.id, data),
    onSuccess: (updatedUser) => {
      updateUser(updatedUser);
      setIsEditing(false);
      queryClient.invalidateQueries({ queryKey: ['user', user?.id] });
      toast({
        title: "Success",
        description: "Profile updated successfully!",
      });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to update profile. Please try again.",
        variant: "destructive",
      });
    },
  });

  const handleSave = () => {
    if (!user) return;
    
    updateProfileMutation.mutate(editedProfile);
  };

  const handleCancel = () => {
    setEditedProfile({
      full_name: user?.full_name || "",
      bio: user?.bio || "",
      location: user?.location || "",
      website: user?.website || "",
    });
    setIsEditing(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (!user) {
    navigate('/');
    return null;
  }

  const isArtist = user.role === 'artist';

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Profile Header */}
          <Card className="mb-8">
            <CardContent className="p-8">
              <div className="flex flex-col md:flex-row gap-6">
                {/* Avatar Section */}
                <div className="flex flex-col items-center md:items-start">
                  <div className="relative">
                    <div className="w-32 h-32 bg-primary/10 rounded-full flex items-center justify-center">
                      {user.avatar_url ? (
                        <img 
                          src={user.avatar_url} 
                          alt={user.full_name || user.username}
                          className="w-full h-full rounded-full object-cover"
                        />
                      ) : (
                        <User className="w-16 h-16 text-primary" />
                      )}
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      className="absolute -bottom-2 -right-2 rounded-full w-8 h-8 p-0"
                      onClick={() => {
                        // TODO: Implement avatar upload
                        toast({
                          title: "Coming Soon",
                          description: "Avatar upload will be available soon!",
                        });
                      }}
                    >
                      <Camera className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  <Badge 
                    variant={isArtist ? "default" : "secondary"}
                    className="mt-3"
                  >
                    {isArtist ? "Artist" : "Enthusiast"}
                  </Badge>
                </div>

                {/* Profile Info */}
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      {isEditing ? (
                        <Input
                          value={editedProfile.full_name}
                          onChange={(e) => setEditedProfile({ ...editedProfile, full_name: e.target.value })}
                          placeholder="Full name"
                          className="text-2xl font-bold mb-2"
                        />
                      ) : (
                        <h1 className="text-3xl font-bold text-foreground mb-2">
                          {user.full_name || user.username}
                        </h1>
                      )}
                      
                      <p className="text-muted-foreground flex items-center mb-2">
                        <User className="w-4 h-4 mr-2" />
                        @{user.username}
                      </p>
                      
                      <p className="text-muted-foreground flex items-center mb-2">
                        <Mail className="w-4 h-4 mr-2" />
                        {user.email}
                      </p>
                      
                      <p className="text-muted-foreground flex items-center">
                        <Calendar className="w-4 h-4 mr-2" />
                        Joined {formatDate(user.created_at)}
                      </p>
                    </div>

                    <div className="flex space-x-2">
                      {isEditing ? (
                        <>
                          <Button 
                            size="sm" 
                            onClick={handleSave}
                            disabled={updateProfileMutation.isPending}
                          >
                            <Save className="w-4 h-4 mr-2" />
                            Save
                          </Button>
                          <Button size="sm" variant="outline" onClick={handleCancel}>
                            <X className="w-4 h-4 mr-2" />
                            Cancel
                          </Button>
                        </>
                      ) : (
                        <Button size="sm" variant="outline" onClick={() => setIsEditing(true)}>
                          <Edit3 className="w-4 h-4 mr-2" />
                          Edit Profile
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Bio */}
                  <div className="mb-4">
                    <Label className="text-sm font-medium text-muted-foreground">Bio</Label>
                    {isEditing ? (
                      <Textarea
                        value={editedProfile.bio}
                        onChange={(e) => setEditedProfile({ ...editedProfile, bio: e.target.value })}
                        placeholder="Tell us about yourself..."
                        rows={3}
                        className="mt-1"
                      />
                    ) : (
                      <p className="text-foreground mt-1">
                        {user.bio || "No bio available"}
                      </p>
                    )}
                  </div>

                  {/* Location and Website */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium text-muted-foreground">Location</Label>
                      {isEditing ? (
                        <Input
                          value={editedProfile.location}
                          onChange={(e) => setEditedProfile({ ...editedProfile, location: e.target.value })}
                          placeholder="Your location"
                          className="mt-1"
                        />
                      ) : (
                        <p className="text-foreground mt-1 flex items-center">
                          <MapPin className="w-4 h-4 mr-2" />
                          {user.location || "Not specified"}
                        </p>
                      )}
                    </div>

                    <div>
                      <Label className="text-sm font-medium text-muted-foreground">Website</Label>
                      {isEditing ? (
                        <Input
                          value={editedProfile.website}
                          onChange={(e) => setEditedProfile({ ...editedProfile, website: e.target.value })}
                          placeholder="https://your-website.com"
                          className="mt-1"
                        />
                      ) : (
                        <div className="mt-1">
                          {user.website ? (
                            <a 
                              href={user.website} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-primary hover:underline"
                            >
                              {user.website}
                            </a>
                          ) : (
                            <span className="text-muted-foreground">Not specified</span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Activity Tabs */}
          <Tabs defaultValue={isArtist ? "paintings" : "ratings"}>
            <TabsList className={`grid w-full ${isArtist ? 'grid-cols-3' : 'grid-cols-2'}`}>
              {isArtist && (
                <TabsTrigger value="paintings">
                  My Paintings ({myPaintings?.total || 0})
                </TabsTrigger>
              )}
              <TabsTrigger value="ratings">
                My Ratings ({myRatings?.total || 0})
              </TabsTrigger>
              <TabsTrigger value="comments">
                My Comments ({myComments?.total || 0})
              </TabsTrigger>
            </TabsList>

            {/* My Paintings Tab (Artists only) */}
            {isArtist && (
              <TabsContent value="paintings">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Palette className="h-5 w-5" />
                      My Paintings
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {myPaintings?.items.length ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {myPaintings.items.map((painting) => (
                          <Card key={painting.id} className="group cursor-pointer hover:shadow-lg transition-shadow">
                            <div 
                              className="aspect-square overflow-hidden rounded-t-lg"
                              onClick={() => navigate(`/painting/${painting.id}`)}
                            >
                              <img
                                src={painting.thumbnail_url || painting.image_url}
                                alt={painting.title}
                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                                onError={(e) => {
                                  e.currentTarget.src = `https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop`;
                                }}
                              />
                            </div>
                            <CardContent className="p-4">
                              <h3 className="font-semibold text-foreground mb-2 line-clamp-1">
                                {painting.title}
                              </h3>
                              
                              <div className="flex items-center justify-between text-sm text-muted-foreground">
                                <div className="flex items-center space-x-3">
                                  <div className="flex items-center">
                                    <Star className="h-3 w-3 mr-1 text-yellow-500" />
                                    <span>{painting.average_rating?.toFixed(1) || '0.0'}</span>
                                  </div>
                                  
                                  <div className="flex items-center">
                                    <Eye className="h-3 w-3 mr-1" />
                                    <span>{painting.view_count}</span>
                                  </div>
                                </div>

                                {painting.price && (
                                  <span className="font-semibold text-primary">
                                    ${painting.price}
                                  </span>
                                )}
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <Palette className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
                        <h3 className="text-lg font-semibold text-foreground mb-2">No paintings yet</h3>
                        <p className="text-muted-foreground mb-4">
                          Start sharing your art with the world!
                        </p>
                        <Button onClick={() => navigate('/dashboard')}>
                          Upload Your First Painting
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            )}

            {/* My Ratings Tab */}
            <TabsContent value="ratings">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Star className="h-5 w-5" />
                    My Ratings
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {myRatings?.items.length ? (
                    <div className="space-y-4">
                      {myRatings.items.map((rating) => (
                        <div key={rating.id} className="flex items-center space-x-4 p-4 border rounded-lg">
                          <div 
                            className="w-16 h-16 rounded-lg overflow-hidden cursor-pointer"
                            onClick={() => navigate(`/painting/${rating.painting.id}`)}
                          >
                            <img
                              src={rating.painting.thumbnail_url || rating.painting.image_url}
                              alt={rating.painting.title}
                              className="w-full h-full object-cover hover:scale-110 transition-transform duration-200"
                              onError={(e) => {
                                e.currentTarget.src = `https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop`;
                              }}
                            />
                          </div>
                          
                          <div className="flex-1">
                            <h4 
                              className="font-semibold text-foreground hover:text-primary cursor-pointer"
                              onClick={() => navigate(`/painting/${rating.painting.id}`)}
                            >
                              {rating.painting.title}
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              by {rating.painting.artist.full_name || rating.painting.artist.username}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Rated on {formatDate(rating.created_at)}
                            </p>
                          </div>
                          
                          <div className="flex items-center">
                            {Array.from({ length: 5 }).map((_, index) => (
                              <Star
                                key={index}
                                className={`h-4 w-4 ${
                                  index < rating.rating 
                                    ? 'text-yellow-500 fill-current' 
                                    : 'text-gray-300'
                                }`}
                              />
                            ))}
                            <span className="ml-2 text-sm font-medium">{rating.rating}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <Star className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
                      <h3 className="text-lg font-semibold text-foreground mb-2">No ratings yet</h3>
                      <p className="text-muted-foreground mb-4">
                        Start exploring the gallery and rate some paintings!
                      </p>
                      <Button onClick={() => navigate('/gallery')}>
                        Explore Gallery
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* My Comments Tab */}
            <TabsContent value="comments">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageSquare className="h-5 w-5" />
                    My Comments
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {myComments?.items.length ? (
                    <div className="space-y-4">
                      {myComments.items.map((comment) => (
                        <div key={comment.id} className="flex space-x-4 p-4 border rounded-lg">
                          <div 
                            className="w-16 h-16 rounded-lg overflow-hidden cursor-pointer"
                            onClick={() => navigate(`/painting/${comment.painting.id}`)}
                          >
                            <img
                              src={comment.painting.thumbnail_url || comment.painting.image_url}
                              alt={comment.painting.title}
                              className="w-full h-full object-cover hover:scale-110 transition-transform duration-200"
                              onError={(e) => {
                                e.currentTarget.src = `https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop`;
                              }}
                            />
                          </div>
                          
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-2">
                              <h4 
                                className="font-semibold text-foreground hover:text-primary cursor-pointer"
                                onClick={() => navigate(`/painting/${comment.painting.id}`)}
                              >
                                {comment.painting.title}
                              </h4>
                              <span className="text-xs text-muted-foreground">
                                {formatDate(comment.created_at)}
                              </span>
                            </div>
                            
                            <p className="text-sm text-muted-foreground mb-2">
                              by {comment.painting.artist.full_name || comment.painting.artist.username}
                            </p>
                            
                            <p className="text-foreground">
                              {comment.content}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <MessageSquare className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
                      <h3 className="text-lg font-semibold text-foreground mb-2">No comments yet</h3>
                      <p className="text-muted-foreground mb-4">
                        Join the conversation by commenting on paintings!
                      </p>
                      <Button onClick={() => navigate('/gallery')}>
                        Explore Gallery
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
};

export default Profile;
