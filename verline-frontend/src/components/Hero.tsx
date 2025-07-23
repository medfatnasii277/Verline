import { Button } from "@/components/ui/button";
import { ArrowRight, Palette, Users } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Link } from "react-router-dom";
import heroImage from "@/assets/hero-gallery.jpg";

export const Hero = () => {
  const { user } = useAuth();
  return (
    <section className="relative min-h-[80vh] flex items-center justify-center overflow-hidden">
      {/* Background Image */}
      <div className="absolute inset-0">
        <img 
          src={heroImage} 
          alt="Elegant gallery interior"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-background/60 backdrop-blur-[1px]" />
      </div>

      {/* Content */}
      <div className="relative z-10 text-center max-w-4xl mx-auto px-4">
        <div className="animate-fade-in">
          <h1 className="text-5xl md:text-7xl font-light text-foreground mb-6 leading-tight">
            Curate.
            <br />
            <span className="text-artwork">Create.</span>
            <br />
            Connect.
          </h1>
          
          <p className="text-xl md:text-2xl text-muted-foreground mb-8 font-light leading-relaxed">
            A sophisticated platform where artists showcase their vision
            <br />
            and enthusiasts discover extraordinary works.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            {!user ? (
              <>
                <Button size="lg" className="bg-artwork text-artwork-foreground hover:bg-artwork/90 shadow-elegant">
                  <Palette className="h-5 w-5 mr-2" />
                  Join as Artist
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
                <Button variant="outline" size="lg" className="border-border hover:bg-gallery">
                  <Users className="h-5 w-5 mr-2" />
                  Explore as Enthusiast
                </Button>
              </>
            ) : (
              <Link to="/gallery">
                <Button size="lg" className="bg-artwork text-artwork-foreground hover:bg-artwork/90 shadow-elegant">
                  Explore Gallery
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
              </Link>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};