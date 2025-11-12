import { MapPin, Users, Star, Calendar } from "lucide-react";
import { Card, CardContent, CardFooter } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Resource } from "../types";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface ResourceCardProps {
  resource: Resource;
  onViewDetails: (resource: Resource) => void;
}

const categoryLabels: Record<string, string> = {
  "study-room": "Study Room",
  "lab-equipment": "Lab Equipment",
  "event-space": "Event Space",
  "av-equipment": "AV Equipment",
  "tutoring": "Tutoring",
  "other": "Other",
};

const categoryColors: Record<string, string> = {
  "study-room": "bg-blue-100 text-blue-800",
  "lab-equipment": "bg-purple-100 text-purple-800",
  "event-space": "bg-green-100 text-green-800",
  "av-equipment": "bg-orange-100 text-orange-800",
  "tutoring": "bg-pink-100 text-pink-800",
  "other": "bg-gray-100 text-gray-800",
};

export function ResourceCard({ resource, onViewDetails }: ResourceCardProps) {
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer" onClick={() => onViewDetails(resource)}>
      <div className="aspect-video relative overflow-hidden bg-gray-100">
        <ImageWithFallback
          src={resource.images[0]}
          alt={resource.title}
          className="w-full h-full object-cover"
        />
        <Badge
          className={`absolute top-3 right-3 ${categoryColors[resource.category] || categoryColors.other}`}
          variant="secondary"
        >
          {categoryLabels[resource.category] || "Other"}
        </Badge>
      </div>
      <CardContent className="p-4">
        <h3 className="mb-2 line-clamp-1">{resource.title}</h3>
        <p className="text-sm text-gray-600 line-clamp-2 mb-3">
          {resource.description}
        </p>
        <div className="space-y-2">
          <div className="flex items-center text-sm text-gray-600">
            <MapPin className="h-4 w-4 mr-2 flex-shrink-0" />
            <span className="line-clamp-1">{resource.location}</span>
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <Users className="h-4 w-4 mr-2 flex-shrink-0" />
            <span>Capacity: {resource.capacity}</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Star className="h-4 w-4 mr-1 text-yellow-500 fill-yellow-500" />
              <span className="text-sm">
                {resource.rating.toFixed(1)} ({resource.reviewCount})
              </span>
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <Calendar className="h-4 w-4 mr-1" />
              <span>{resource.bookingCount} bookings</span>
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter className="p-4 pt-0">
        <Button
          className="w-full"
          onClick={(e) => {
            e.stopPropagation();
            onViewDetails(resource);
          }}
        >
          View Details
        </Button>
      </CardFooter>
    </Card>
  );
}
