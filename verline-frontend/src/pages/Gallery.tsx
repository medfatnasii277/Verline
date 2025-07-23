import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Star, MessageCircle, Eye, User, Search, Filter } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { api, Painting, Category } from "@/services/api";
import { useNavigate } from "react-router-dom";
import { Header } from "@/components/Header";
import { useToast } from "@/hooks/use-toast";

const Gallery = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [currentPage, setCurrentPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  
  const itemsPerPage = 12;

  // Fetch paintings
  const { data: paintingsData, isLoading: paintingsLoading, error: paintingsError } = useQuery({
    queryKey: ['paintings', currentPage, selectedCategory, itemsPerPage],
    queryFn: () => api.paintings.getAll(
      currentPage, 
      itemsPerPage, 
      selectedCategory ? parseInt(selectedCategory) : undefined
    ),
  });

  // Fetch categories
  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: api.categories.getAll,
  });

  // Filter paintings by search term locally
  const filteredPaintings = paintingsData?.items.filter(painting =>
    painting.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    painting.artist.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    painting.description?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const handlePaintingClick = (paintingId: number) => {
    navigate(`/painting/${paintingId}`);
  };

  const handleCategoryChange = (categoryId: string) => {
    setSelectedCategory(categoryId);
    setCurrentPage(1); // Reset to first page when category changes
  };

  const formatRating = (rating: number | undefined) => {
    return rating ? rating.toFixed(1) : '0.0';
  };

  if (paintingsError) {
    toast({
      title: "Error",
      description: "Failed to load paintings. Please try again.",
      variant: "destructive",
    });
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <h1 className="text-4xl font-light text-foreground mb-4">Art Gallery</h1>
          <p className="text-muted-foreground text-lg">
            Discover amazing artworks from talented artists around the world
          </p>
        </div>

        {/* Search and Filters */}
        <div className="mb-8 space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Search Input */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search paintings, artists..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Filter Toggle Button */}
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2"
            >
              <Filter className="h-4 w-4" />
              Filters
            </Button>
          </div>

          {/* Filters */}
          {showFilters && (
            <div className="flex flex-col sm:flex-row gap-4 p-4 bg-muted rounded-lg">
              <div className="flex-1">
                <Select value={selectedCategory} onValueChange={handleCategoryChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Categories</SelectItem>
                    {categories?.map((category) => (
                      <SelectItem key={category.id} value={category.id.toString()}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {selectedCategory && (
                <Button 
                  variant="ghost" 
                  onClick={() => handleCategoryChange("")}
                  className="text-sm"
                >
                  Clear Filters
                </Button>
              )}
            </div>
          )}
        </div>

        {/* Results Summary */}
        <div className="mb-6">
          <p className="text-muted-foreground">
            {paintingsLoading ? 'Loading...' : `Showing ${filteredPaintings.length} of ${paintingsData?.total || 0} paintings`}
            {selectedCategory && (
              <span className="ml-2">
                in {categories?.find(c => c.id.toString() === selectedCategory)?.name}
              </span>
            )}
          </p>
        </div>

        {/* Paintings Grid */}
        {paintingsLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {Array.from({ length: itemsPerPage }).map((_, index) => (
              <Card key={index} className="animate-pulse">
                <div className="aspect-[3/4] bg-muted rounded-t-lg"></div>
                <CardContent className="p-4">
                  <div className="h-4 bg-muted rounded mb-2"></div>
                  <div className="h-3 bg-muted rounded mb-1"></div>
                  <div className="h-3 bg-muted rounded w-3/4"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredPaintings.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredPaintings.map((painting) => (
              <Card 
                key={painting.id} 
                className="group cursor-pointer hover:shadow-lg transition-all duration-200"
                onClick={() => handlePaintingClick(painting.id)}
              >
                <div className="aspect-[3/4] overflow-hidden rounded-t-lg bg-muted">
                  <img
                    src={painting.thumbnail_url || painting.image_url}
                    alt={painting.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                    onError={(e) => {
                      e.currentTarget.src = `https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=500&fit=crop`;
                    }}
                  />
                </div>
                <CardContent className="p-4">
                  <h3 className="font-semibold text-foreground mb-2 line-clamp-1">
                    {painting.title}
                  </h3>
                  
                  <div className="flex items-center text-sm text-muted-foreground mb-2">
                    <User className="h-3 w-3 mr-1" />
                    <span>{painting.artist.full_name}</span>
                  </div>

                  {painting.category && (
                    <Badge variant="secondary" className="text-xs mb-2">
                      {painting.category.name}
                    </Badge>
                  )}

                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <div className="flex items-center space-x-3">
                      <div className="flex items-center">
                        <Star className="h-3 w-3 mr-1 fill-current text-yellow-500" />
                        <span>{formatRating(painting.average_rating)}</span>
                        <span className="ml-1">({painting.rating_count})</span>
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
          <div className="text-center py-12">
            <p className="text-muted-foreground text-lg">
              No paintings found matching your criteria.
            </p>
            {(searchTerm || selectedCategory) && (
              <Button 
                variant="ghost" 
                onClick={() => {
                  setSearchTerm("");
                  setSelectedCategory("");
                }}
                className="mt-4"
              >
                Clear all filters
              </Button>
            )}
          </div>
        )}

        {/* Pagination */}
        {paintingsData && paintingsData.pages > 1 && (
          <div className="flex justify-center items-center space-x-2 mt-8">
            <Button
              variant="outline"
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            
            <div className="flex items-center space-x-1">
              {Array.from({ length: Math.min(5, paintingsData.pages) }, (_, i) => {
                const pageNum = i + 1;
                return (
                  <Button
                    key={pageNum}
                    variant={currentPage === pageNum ? "default" : "ghost"}
                    size="sm"
                    onClick={() => setCurrentPage(pageNum)}
                  >
                    {pageNum}
                  </Button>
                );
              })}
            </div>

            <Button
              variant="outline"
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage === paintingsData.pages}
            >
              Next
            </Button>
          </div>
        )}
      </main>
    </div>
  );
};

export default Gallery;
