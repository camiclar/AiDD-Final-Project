import { Calendar, Clock, MapPin, MoreVertical } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Booking, Resource } from "../types";

interface BookingsViewProps {
  bookings: Booking[];
  resources: Resource[];
  onCancelBooking: (bookingId: string) => void;
  onViewResource: (resourceId: string) => void;
}

export function BookingsView({
  bookings,
  resources,
  onCancelBooking,
  onViewResource,
}: BookingsViewProps) {
  const now = new Date();

  const upcomingBookings = bookings.filter(
    (b) => b.startTime > now && (b.status === "approved" || b.status === "pending")
  );
  const pastBookings = bookings.filter(
    (b) => b.endTime < now || b.status === "completed"
  );
  const pendingBookings = bookings.filter((b) => b.status === "pending");

  const getStatusVariant = (status: string) => {
    switch (status) {
      case "approved":
        return "default";
      case "pending":
        return "secondary";
      case "rejected":
        return "destructive";
      case "cancelled":
        return "outline";
      default:
        return "secondary";
    }
  };

  const getResourceDetails = (resourceId: string) => {
    return resources.find((r) => r.id === resourceId);
  };

  const renderBookingCard = (booking: Booking) => {
    const resource = getResourceDetails(booking.resourceId);

    return (
      <Card key={booking.id}>
        <CardContent className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h3 className="mb-2">{booking.resourceTitle}</h3>
              <div className="flex items-center gap-2 mb-2">
                <Badge variant={getStatusVariant(booking.status)}>
                  {booking.status}
                </Badge>
                {booking.recurrence !== "none" && (
                  <Badge variant="outline">{booking.recurrence}</Badge>
                )}
              </div>
            </div>
            {booking.status !== "cancelled" && booking.status !== "rejected" && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem
                    onClick={() => onViewResource(booking.resourceId)}
                  >
                    View Resource
                  </DropdownMenuItem>
                  {booking.status !== "completed" && (
                    <DropdownMenuItem
                      onClick={() => onCancelBooking(booking.id)}
                      className="text-red-600"
                    >
                      Cancel Booking
                    </DropdownMenuItem>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex items-center text-gray-600">
              <Calendar className="h-4 w-4 mr-2" />
              <span>{booking.startTime.toLocaleDateString()}</span>
            </div>
            <div className="flex items-center text-gray-600">
              <Clock className="h-4 w-4 mr-2" />
              <span>
                {booking.startTime.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}{" "}
                -{" "}
                {booking.endTime.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
            {resource && (
              <div className="flex items-center text-gray-600">
                <MapPin className="h-4 w-4 mr-2" />
                <span>{resource.location}</span>
              </div>
            )}
          </div>

          {booking.notes && (
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Notes: </span>
                {booking.notes}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl mb-2">My Bookings</h1>
        <p className="text-gray-600">Manage your resource reservations</p>
      </div>

      <Tabs defaultValue="upcoming">
        <TabsList>
          <TabsTrigger value="upcoming">
            Upcoming ({upcomingBookings.length})
          </TabsTrigger>
          <TabsTrigger value="pending">
            Pending ({pendingBookings.length})
          </TabsTrigger>
          <TabsTrigger value="past">
            Past ({pastBookings.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="upcoming" className="space-y-4 mt-6">
          {upcomingBookings.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p className="text-gray-500 mb-2">No upcoming bookings</p>
                <p className="text-sm text-gray-400">
                  Browse resources to make a reservation
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {upcomingBookings.map((booking) => renderBookingCard(booking))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="pending" className="space-y-4 mt-6">
          {pendingBookings.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Clock className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p className="text-gray-500">No pending bookings</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {pendingBookings.map((booking) => renderBookingCard(booking))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="past" className="space-y-4 mt-6">
          {pastBookings.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p className="text-gray-500">No past bookings</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {pastBookings.map((booking) => renderBookingCard(booking))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
