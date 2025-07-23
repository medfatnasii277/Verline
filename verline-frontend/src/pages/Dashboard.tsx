import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Upload, 
  Image as ImageIcon, 
  Edit, 
  Trash2, 
  Eye, 
  Star, 
  Plus,
  FileImage,
  DollarSign,
  Calendar,
  Palette
} from "lucide-react";
import { api, Painting, Category } from "@/services/api";
import { useAuth } from "@/contexts/AuthContext";
import { Header } from "@/components/Header";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [newPainting, setNewPainting] = useState({
    title: "",
    description: "",
    category_id: "",
    price: "",
    year_created: new Date().getFullYear().toString(),
    dimensions: "",
    medium: "",
    status: "published" as "draft" | "published" | "archived",
    tags: "",
  });

  // Redirect if not an artist
  useEffect(() => {
    if (user && user.role !== 'artist') {
      navigate('/gallery');
      toast({
        title: "Access Denied",
        description: "Only artists can access the dashboard.",
        variant: "destructive",
      });
    }
  }, [user, navigate, toast]);

  // Fetch artist's paintings
  const { data: myPaintings, isLoading: paintingsLoading } = useQuery({
    queryKey: ['myPaintings', user?.id],
    queryFn: () => user ? api.paintings.getMyPaintings(user.id) : Promise.resolve({ items: [], total: 0, page: 1, pages: 1 }),
    enabled: !!user && user.role === 'artist',
  });

  // Fetch categories
  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: api.categories.getAll,
  });

  // Upload painting mutation
  const uploadMutation = useMutation({
    mutationFn: (formData: FormData) => api.paintings.create(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['myPaintings'] });
      resetForm();
      toast({
        title: "Success",
        description: "Painting uploaded successfully!",
      });
    },
    onError: (error) => {
      console.error('Upload error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to upload painting. Please try again.';
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    },
  });

  // Delete painting mutation
  const deleteMutation = useMutation({
    mutationFn: ({ paintingId, artistId }: { paintingId: number; artistId: number }) => {
      console.log('Delete mutation started for painting ID:', paintingId, 'by artist:', artistId);
      return api.paintings.delete(paintingId, artistId);
    },
    onSuccess: () => {
      console.log('Delete mutation successful');
      queryClient.invalidateQueries({ queryKey: ['myPaintings'] });
      toast({
        title: "Success",
        description: "Painting deleted successfully!",
      });
    },
    onError: (error) => {
      console.error('Delete mutation error:', error);
      toast({
        title: "Error",
        description: `Failed to delete painting: ${error.message}`,
        variant: "destructive",
      });
    },
  });

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  const resetForm = () => {
    setNewPainting({
      title: "",
      description: "",
      category_id: "",
      price: "",
      year_created: new Date().getFullYear().toString(),
      dimensions: "",
      medium: "",
      status: "published",
      tags: "",
    });
    setSelectedFile(null);
    setPreviewUrl("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile) {
      toast({
        title: "Error",
        description: "Please select an image file.",
        variant: "destructive",
      });
      return;
    }

    if (!newPainting.title.trim()) {
      toast({
        title: "Error",
        description: "Please enter a title for your painting.",
        variant: "destructive",
      });
      return;
    }

    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('title', newPainting.title.trim());
    formData.append('artist_id', user.id.toString()); // Add the required artist_id
    
    if (newPainting.description) formData.append('description', newPainting.description);
    if (newPainting.category_id) formData.append('category_id', newPainting.category_id);
    if (newPainting.price) formData.append('price', newPainting.price);
    if (newPainting.year_created) formData.append('year_created', newPainting.year_created);
    if (newPainting.dimensions) formData.append('dimensions', newPainting.dimensions);
    if (newPainting.medium) formData.append('medium', newPainting.medium);
    if (newPainting.tags) formData.append('tags', newPainting.tags);
    formData.append('status', newPainting.status);

    uploadMutation.mutate(formData);
  };

  const handleDelete = (paintingId: number) => {
    console.log('handleDelete called with paintingId:', paintingId);
    if (!user) {
      console.error('No user found for delete operation');
      toast({
        title: "Error",
        description: "You must be logged in to delete paintings.",
        variant: "destructive",
      });
      return;
    }
    
    if (window.confirm('Are you sure you want to delete this painting? This action cannot be undone.')) {
      console.log('User confirmed delete, calling mutation with artistId:', user.id);
      deleteMutation.mutate({ paintingId, artistId: user.id });
    } else {
      console.log('User cancelled delete');
    }
  };

  const formatPrice = (price: number | undefined) => {
    return price ? `$${price.toFixed(2)}` : 'Not for sale';
  };

  if (!user || user.role !== 'artist') {
    return null; // Will redirect via useEffect
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-light text-foreground mb-4">Artist Dashboard</h1>
          <p className="text-muted-foreground text-lg">
            Manage your artwork and track your gallery presence
          </p>
        </div>

        <Tabs defaultValue="upload" className="space-y-8">
          <TabsList className="grid w-full grid-cols-3 max-w-md">
            <TabsTrigger value="upload">Upload Art</TabsTrigger>
            <TabsTrigger value="gallery">My Gallery</TabsTrigger>
            <TabsTrigger value="stats">Statistics</TabsTrigger>
          </TabsList>

          {/* Upload New Painting */}
          <TabsContent value="upload">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  Upload New Painting
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* File Upload */}
                  <div className="space-y-4">
                    <Label htmlFor="image">Artwork Image *</Label>
                    <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
                      {previewUrl ? (
                        <div className="space-y-4">
                          <img
                            src={previewUrl}
                            alt="Preview"
                            className="max-w-sm max-h-64 mx-auto rounded-lg shadow-md"
                          />
                          <Button 
                            type="button" 
                            variant="outline" 
                            onClick={() => {
                              setSelectedFile(null);
                              setPreviewUrl("");
                            }}
                          >
                            Change Image
                          </Button>
                        </div>
                      ) : (
                        <div className="space-y-4">
                          <FileImage className="h-16 w-16 mx-auto text-muted-foreground" />
                          <div>
                            <Label htmlFor="image" className="cursor-pointer">
                              <span className="text-primary hover:text-primary/80">
                                Click to upload
                              </span>
                              <span className="text-muted-foreground"> or drag and drop</span>
                            </Label>
                            <p className="text-sm text-muted-foreground mt-2">
                              PNG, JPG, GIF up to 10MB
                            </p>
                          </div>
                        </div>
                      )}
                      <Input
                        id="image"
                        type="file"
                        accept="image/*"
                        onChange={handleFileSelect}
                        className="hidden"
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Title */}
                    <div className="space-y-2">
                      <Label htmlFor="title">Title *</Label>
                      <Input
                        id="title"
                        value={newPainting.title}
                        onChange={(e) => setNewPainting({ ...newPainting, title: e.target.value })}
                        placeholder="Enter painting title"
                        required
                      />
                    </div>

                    {/* Category */}
                    <div className="space-y-2">
                      <Label htmlFor="category">Category</Label>
                      <Select 
                        value={newPainting.category_id} 
                        onValueChange={(value) => setNewPainting({ ...newPainting, category_id: value })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select category" />
                        </SelectTrigger>
                        <SelectContent>
                          {categories?.map((category) => (
                            <SelectItem key={category.id} value={category.id.toString()}>
                              {category.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Price */}
                    <div className="space-y-2">
                      <Label htmlFor="price">Price (USD)</Label>
                      <Input
                        id="price"
                        type="number"
                        step="0.01"
                        min="0"
                        value={newPainting.price}
                        onChange={(e) => setNewPainting({ ...newPainting, price: e.target.value })}
                        placeholder="0.00"
                      />
                    </div>

                    {/* Year Created */}
                    <div className="space-y-2">
                      <Label htmlFor="year">Year Created</Label>
                      <Input
                        id="year"
                        type="number"
                        min="1900"
                        max={new Date().getFullYear()}
                        value={newPainting.year_created}
                        onChange={(e) => setNewPainting({ ...newPainting, year_created: e.target.value })}
                      />
                    </div>

                    {/* Dimensions */}
                    <div className="space-y-2">
                      <Label htmlFor="dimensions">Dimensions</Label>
                      <Input
                        id="dimensions"
                        value={newPainting.dimensions}
                        onChange={(e) => setNewPainting({ ...newPainting, dimensions: e.target.value })}
                        placeholder="e.g., 24x36 inches"
                      />
                    </div>

                    {/* Medium */}
                    <div className="space-y-2">
                      <Label htmlFor="medium">Medium</Label>
                      <Input
                        id="medium"
                        value={newPainting.medium}
                        onChange={(e) => setNewPainting({ ...newPainting, medium: e.target.value })}
                        placeholder="e.g., Oil on canvas"
                      />
                    </div>
                  </div>

                  {/* Description */}
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={newPainting.description}
                      onChange={(e) => setNewPainting({ ...newPainting, description: e.target.value })}
                      placeholder="Describe your artwork..."
                      rows={4}
                    />
                  </div>

                  {/* Tags */}
                  <div className="space-y-2">
                    <Label htmlFor="tags">Tags</Label>
                    <Input
                      id="tags"
                      value={newPainting.tags}
                      onChange={(e) => setNewPainting({ ...newPainting, tags: e.target.value })}
                      placeholder="landscape, nature, sunset (comma-separated)"
                    />
                  </div>

                  {/* Status */}
                  <div className="space-y-2">
                    <Label htmlFor="status">Status</Label>
                    <Select 
                      value={newPainting.status} 
                      onValueChange={(value: "draft" | "published" | "archived") => 
                        setNewPainting({ ...newPainting, status: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="draft">Draft</SelectItem>
                        <SelectItem value="published">Published</SelectItem>
                        <SelectItem value="archived">Archived</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="flex gap-4">
                    <Button 
                      type="submit" 
                      disabled={uploadMutation.isPending}
                      className="flex-1"
                    >
                      {uploadMutation.isPending ? 'Uploading...' : 'Upload Painting'}
                    </Button>
                    <Button type="button" variant="outline" onClick={resetForm}>
                      Reset
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* My Gallery */}
          <TabsContent value="gallery">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ImageIcon className="h-5 w-5" />
                  My Gallery ({myPaintings?.total || 0} paintings)
                </CardTitle>
              </CardHeader>
              <CardContent>
                {paintingsLoading ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {Array.from({ length: 6 }).map((_, index) => (
                      <Card key={index} className="animate-pulse">
                        <div className="aspect-square bg-muted rounded-t-lg"></div>
                        <CardContent className="p-4">
                          <div className="h-4 bg-muted rounded mb-2"></div>
                          <div className="h-3 bg-muted rounded w-3/4"></div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : myPaintings?.items.length ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {myPaintings.items.map((painting) => (
                      <Card key={painting.id} className="group hover:shadow-lg transition-shadow">
                        <div className="aspect-square overflow-hidden rounded-t-lg">
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
                          
                          <div className="flex items-center justify-between text-sm text-muted-foreground mb-2">
                            <Badge variant={
                              painting.status === 'published' ? 'default' :
                              painting.status === 'draft' ? 'secondary' : 'outline'
                            }>
                              {painting.status}
                            </Badge>
                            
                            {painting.category && (
                              <span>{painting.category.name}</span>
                            )}
                          </div>

                          <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
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

                          <div className="flex space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => navigate(`/painting/${painting.id}`)}
                              className="flex-1"
                            >
                              <Eye className="h-3 w-3 mr-1" />
                              View
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDelete(painting.id)}
                              disabled={deleteMutation.isPending}
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <ImageIcon className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
                    <h3 className="text-lg font-semibold text-foreground mb-2">No paintings yet</h3>
                    <p className="text-muted-foreground mb-4">
                      Upload your first painting to get started!
                    </p>
                    <Button onClick={() => {
                      const uploadTab = document.querySelector('[data-value="upload"]') as HTMLElement;
                      uploadTab?.click();
                    }}>
                      <Plus className="h-4 w-4 mr-2" />
                      Upload Painting
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Statistics */}
          <TabsContent value="stats">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Paintings</p>
                      <p className="text-2xl font-bold">{myPaintings?.total || 0}</p>
                    </div>
                    <ImageIcon className="h-8 w-8 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Views</p>
                      <p className="text-2xl font-bold">
                        {myPaintings?.items.reduce((sum, p) => sum + p.view_count, 0) || 0}
                      </p>
                    </div>
                    <Eye className="h-8 w-8 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Average Rating</p>
                      <p className="text-2xl font-bold">
                        {myPaintings?.items.length ? 
                          (myPaintings.items.reduce((sum, p) => sum + (p.average_rating || 0), 0) / myPaintings.items.length).toFixed(1) 
                          : '0.0'
                        }
                      </p>
                    </div>
                    <Star className="h-8 w-8 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Ratings</p>
                      <p className="text-2xl font-bold">
                        {myPaintings?.items.reduce((sum, p) => sum + p.rating_count, 0) || 0}
                      </p>
                    </div>
                    <Star className="h-8 w-8 text-muted-foreground" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Dashboard;
