import { Calendar, Star, TrendingUp, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { User, Booking, Resource } from "../types";

interface DashboardViewProps {
  user: User;
  upcomingBookings: Booking[];
  recentResources: Resource[];
  onNavigate: (view: string) => void;
  onViewResource: (resource: Resource) => void;
}

export function DashboardView({
  user,
  upcomingBookings,
  recentResources,
  onNavigate,
  onViewResource,
}: DashboardViewProps) {
  const stats = [
    {
      title: "Active Bookings",
      value: upcomingBookings.length,
      icon: Calendar,
      color: "text-blue-600",
    },
    {
      title: "Resources Available",
      value: recentResources.filter(r => r.status === "published").length,
      icon: Star,
      color: "text-yellow-600",
    },
    {
      title: "Pending Approvals",
      value: upcomingBookings.filter(b => b.status === "pending").length,
      icon: Clock,
      color: "text-orange-600",
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl mb-2">Welcome back, {user.name.split(" ")[0]}!</h1>
        <p className="text-gray-600">Here's what's happening with your campus resources</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">{stat.title}</p>
                    <p className="text-3xl">{stat.value}</p>
                  </div>
                  <Icon className={`h-12 w-12 ${stat.color}`} />
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Upcoming Bookings */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Upcoming Bookings</CardTitle>
          <Button variant="ghost" onClick={() => onNavigate("bookings")}>
            View All
          </Button>
        </CardHeader>
        <CardContent>
          {upcomingBookings.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Calendar className="h-12 w-12 mx-auto mb-2 text-gray-300" />
              <p>No upcoming bookings</p>
              <Button
                variant="link"
                onClick={() => onNavigate("resources")}
                className="mt-2"
              >
                Browse resources to book
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {upcomingBookings.slice(0, 3).map((booking) => (
                <div
                  key={booking.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <p>{booking.resourceTitle}</p>
                    <p className="text-sm text-gray-600">
                      {booking.startTime.toLocaleDateString()} at{" "}
                      {booking.startTime.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  </div>
                  <Badge
                    variant={
                      booking.status === "approved"
                        ? "default"
                        : booking.status === "pending"
                        ? "secondary"
                        : "destructive"
                    }
                  >
                    {booking.status}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Popular Resources */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Popular Resources</CardTitle>
          <Button variant="ghost" onClick={() => onNavigate("resources")}>
            Browse All
          </Button>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recentResources.slice(0, 4).map((resource) => (
              <div
                key={resource.id}
                className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                onClick={() => onViewResource(resource)}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-sm line-clamp-1">{resource.title}</h3>
                  <div className="flex items-center">
                    <Star className="h-3 w-3 text-yellow-500 fill-yellow-500 mr-1" />
                    <span className="text-sm">{resource.rating.toFixed(1)}</span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 line-clamp-2">
                  {resource.description}
                </p>
                <div className="mt-2">
                  <Badge variant="secondary" className="text-xs">
                    {resource.category.split("-").join(" ")}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      {(user.role === "staff" || user.role === "admin") && (
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Button onClick={() => onNavigate("create-resource")}>
                Create New Resource
              </Button>
              <Button variant="outline" onClick={() => onNavigate("my-resources")}>
                Manage My Resources
              </Button>
              {user.role === "admin" && (
                <Button variant="outline" onClick={() => onNavigate("admin")}>
                  Admin Panel
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
