import { useState } from "react";
import { MapPin, Users, Star, Calendar as CalendarIcon, Clock, Shield, X, MessageCircle } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Resource, Review, User } from "../types";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { BookingForm } from "./booking-form";

interface ResourceDetailModalProps {
  resource: Resource;
  reviews: Review[];
  currentUser: User;
  onClose: () => void;
  onBook: (resourceId: string, startTime: Date, endTime: Date, notes: string, recurrence: string) => void;
  onMessageOwner?: () => void;
}

const categoryLabels: Record<string, string> = {
  "study-room": "Study Room",
  "lab-equipment": "Lab Equipment",
  "event-space": "Event Space",
  "av-equipment": "AV Equipment",
  "tutoring": "Tutoring",
  "other": "Other",
};

export function ResourceDetailModal({
  resource,
  reviews,
  currentUser,
  onClose,
  onBook,
  onMessageOwner,
}: ResourceDetailModalProps) {
  const [showBookingForm, setShowBookingForm] = useState(false);

  const handleBook = (startTime: Date, endTime: Date, notes: string, recurrence: string) => {
    onBook(resource.id, startTime, endTime, notes, recurrence);
    setShowBookingForm(false);
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <DialogTitle className="text-2xl mb-2">{resource.title}</DialogTitle>
              <div className="flex items-center gap-2">
                <Badge>{categoryLabels[resource.category]}</Badge>
                {resource.requiresApproval && (
                  <Badge variant="outline">
                    <Shield className="h-3 w-3 mr-1" />
                    Requires Approval
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Image */}
          <div className="aspect-video relative overflow-hidden rounded-lg bg-gray-100">
            <ImageWithFallback
              src={resource.images[0]}
              alt={resource.title}
              className="w-full h-full object-cover"
            />
          </div>

          {/* Quick Info */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-gray-500" />
              <div>
                <p className="text-xs text-gray-500">Location</p>
                <p className="text-sm">{resource.location}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-gray-500" />
              <div>
                <p className="text-xs text-gray-500">Capacity</p>
                <p className="text-sm">{resource.capacity} people</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
              <div>
                <p className="text-xs text-gray-500">Rating</p>
                <p className="text-sm">{resource.rating.toFixed(1)} ({resource.reviewCount})</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <CalendarIcon className="h-5 w-5 text-gray-500" />
              <div>
                <p className="text-xs text-gray-500">Bookings</p>
                <p className="text-sm">{resource.bookingCount} total</p>
              </div>
            </div>
          </div>

          <Separator />

          {/* Booking Section */}
          {!showBookingForm && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="mb-1">Ready to book?</h3>
                  <p className="text-sm text-gray-700">
                    {resource.requiresApproval 
                      ? `Requires approval from ${resource.ownerName}` 
                      : 'Instant booking available'}
                  </p>
                </div>
              </div>
              <Button
                className="w-full"
                size="lg"
                onClick={() => setShowBookingForm(true)}
              >
                Continue to Booking
              </Button>
            </div>
          )}

          {showBookingForm && (
            <div className="border rounded-lg p-4">
              <BookingForm
                resource={resource}
                onSubmit={handleBook}
                onCancel={() => setShowBookingForm(false)}
              />
            </div>
          )}

          {/* Tabs */}
          <Tabs defaultValue="details">
            <TabsList>
              <TabsTrigger value="details">Details</TabsTrigger>
              <TabsTrigger value="reviews">Reviews ({reviews.length})</TabsTrigger>
            </TabsList>

            <TabsContent value="details" className="space-y-4">
              <div>
                <h3 className="mb-2">Description</h3>
                <p className="text-gray-600">{resource.description}</p>
              </div>

              {resource.equipment && resource.equipment.length > 0 && (
                <div>
                  <h3 className="mb-2">Equipment & Amenities</h3>
                  <div className="flex flex-wrap gap-2">
                    {resource.equipment.map((item, index) => (
                      <Badge key={index} variant="secondary">
                        {item}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h3 className="mb-2">Availability</h3>
                <div className="flex items-start gap-2 text-gray-600">
                  <Clock className="h-5 w-5 mt-0.5" />
                  <p>{resource.availabilityRules}</p>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3>Managed By</h3>
                  {onMessageOwner && currentUser.id !== resource.ownerId && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={onMessageOwner}
                    >
                      <MessageCircle className="h-4 w-4 mr-2" />
                      Message Owner
                    </Button>
                  )}
                </div>
                <p className="text-gray-600">{resource.ownerName}</p>
              </div>
            </TabsContent>

            <TabsContent value="reviews" className="space-y-4">
              {reviews.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No reviews yet. Be the first to review this resource!
                </div>
              ) : (
                <div className="space-y-4">
                  {reviews.map((review) => (
                    <div key={review.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <p>{review.userName}</p>
                          <p className="text-sm text-gray-500">
                            {review.createdAt.toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex items-center">
                          <Star className="h-4 w-4 text-yellow-500 fill-yellow-500 mr-1" />
                          <span>{review.rating.toFixed(1)}</span>
                        </div>
                      </div>
                      <p className="text-gray-600">{review.comment}</p>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  );
}