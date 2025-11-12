import { useState, useEffect } from "react";
import { Toaster } from "./components/ui/sonner";
import { toast } from "sonner@2.0.3";
import { AuthForm } from "./components/auth-form";
import { Header } from "./components/header";
import { Navigation } from "./components/navigation";
import { DashboardView } from "./components/dashboard-view";
import { ResourcesView } from "./components/resources-view";
import { ResourceDetailModal } from "./components/resource-detail-modal";
import { BookingsView } from "./components/bookings-view";
import { MessagesView } from "./components/messages-view";
import { AdminView } from "./components/admin-view";
import { CreateResourceForm } from "./components/create-resource-form";
import { ProfileSettings } from "./components/profile-settings";
import {
  mockUsers,
  mockResources,
  mockBookings,
  mockReviews,
  mockMessages,
  mockNotifications,
} from "./lib/mock-data";
import {
  User,
  Resource,
  Booking,
  Review,
  Message,
  Notification,
  UserRole,
} from "./types";

export default function App() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [currentView, setCurrentView] = useState("dashboard");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);

  // Mock data state
  const [users, setUsers] = useState<User[]>(mockUsers);
  const [resources, setResources] = useState<Resource[]>(mockResources);
  const [bookings, setBookings] = useState<Booking[]>(mockBookings);
  const [reviews, setReviews] = useState<Review[]>(mockReviews);
  const [messages, setMessages] = useState<Message[]>(mockMessages);
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications);

  // Authentication handlers
  const handleLogin = (email: string, password: string) => {
    const user = users.find((u) => u.email === email);
    if (user) {
      setCurrentUser(user);
      toast.success(`Welcome back, ${user.name}!`);
    } else {
      toast.error("Invalid credentials. Try one of the demo accounts.");
    }
  };

  const handleSignup = (
    email: string,
    password: string,
    name: string,
    role: UserRole,
    department?: string,
    profileImage?: string
  ) => {
    const newUser: User = {
      id: `user-${Date.now()}`,
      email,
      name,
      role,
      department,
      profileImage,
      createdAt: new Date(),
    };
    setUsers([...users, newUser]);
    setCurrentUser(newUser);
    toast.success("Account created successfully!");
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setCurrentView("dashboard");
    toast.success("Logged out successfully");
  };

  // Profile update handler
  const handleUpdateProfile = (updates: Partial<User>) => {
    if (!currentUser) return;
    
    const updatedUser = { ...currentUser, ...updates };
    setCurrentUser(updatedUser);
    setUsers(users.map(u => u.id === currentUser.id ? updatedUser : u));
  };

  // Navigation handler
  const handleNavigate = (view: string) => {
    if (view.startsWith("/")) {
      view = view.substring(1);
    }
    setCurrentView(view);
    setSearchQuery("");
  };

  // Resource handlers
  const handleViewResourceDetails = (resource: Resource) => {
    setSelectedResource(resource);
  };

  const handleCloseResourceDetails = () => {
    setSelectedResource(null);
  };

  const handleCreateResource = (resourceData: any) => {
    const newResource: Resource = {
      id: `r-${Date.now()}`,
      ...resourceData,
      images: resourceData.imageUrl 
        ? [resourceData.imageUrl] 
        : [mockResources[0].images[0]], // Use placeholder image if no image provided
      status: "published" as const,
      rating: 0,
      reviewCount: 0,
      bookingCount: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setResources([...resources, newResource]);
    toast.success("Resource created successfully!");
    setCurrentView("my-resources");
  };

  const handleDeleteResource = (resourceId: string) => {
    setResources(
      resources.map((r) =>
        r.id === resourceId ? { ...r, status: "archived" as const } : r
      )
    );
    toast.success("Resource archived");
  };

  // Booking handlers
  const handleBookResource = (
    resourceId: string,
    startTime: Date,
    endTime: Date,
    notes: string,
    recurrence: string
  ) => {
    if (!currentUser) return;

    const resource = resources.find((r) => r.id === resourceId);
    if (!resource) return;

    const newBooking: Booking = {
      id: `b-${Date.now()}`,
      resourceId,
      resourceTitle: resource.title,
      userId: currentUser.id,
      userName: currentUser.name,
      startTime,
      endTime,
      status: resource.requiresApproval ? "pending" : "approved",
      notes,
      recurrence: recurrence as any,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    setBookings([...bookings, newBooking]);

    // Update resource booking count
    setResources(
      resources.map((r) =>
        r.id === resourceId ? { ...r, bookingCount: r.bookingCount + 1 } : r
      )
    );

    // Create notification
    const notification: Notification = {
      id: `n-${Date.now()}`,
      userId: currentUser.id,
      type: resource.requiresApproval ? "booking_pending" : "booking_confirmed",
      title: resource.requiresApproval
        ? "Booking Pending Approval"
        : "Booking Confirmed",
      message: resource.requiresApproval
        ? `Your booking for ${resource.title} is pending approval from ${resource.ownerName}.`
        : `Your booking for ${resource.title} has been confirmed.`,
      read: false,
      link: "/bookings",
      createdAt: new Date(),
    };
    setNotifications([notification, ...notifications]);

    toast.success(
      resource.requiresApproval
        ? "Booking submitted for approval"
        : "Booking confirmed!"
    );
    setSelectedResource(null);
    setCurrentView("bookings");
  };

  const handleCancelBooking = (bookingId: string) => {
    setBookings(
      bookings.map((b) =>
        b.id === bookingId ? { ...b, status: "cancelled" as const } : b
      )
    );
    toast.success("Booking cancelled");
  };

  const handleApproveBooking = (bookingId: string) => {
    const booking = bookings.find((b) => b.id === bookingId);
    if (!booking) return;

    setBookings(
      bookings.map((b) =>
        b.id === bookingId ? { ...b, status: "approved" as const } : b
      )
    );

    const notification: Notification = {
      id: `n-${Date.now()}`,
      userId: booking.userId,
      type: "booking_approved",
      title: "Booking Approved",
      message: `Your booking for ${booking.resourceTitle} has been approved!`,
      read: false,
      link: "/bookings",
      createdAt: new Date(),
    };
    setNotifications([notification, ...notifications]);

    toast.success("Booking approved");
  };

  const handleRejectBooking = (bookingId: string) => {
    const booking = bookings.find((b) => b.id === bookingId);
    if (!booking) return;

    setBookings(
      bookings.map((b) =>
        b.id === bookingId ? { ...b, status: "rejected" as const } : b
      )
    );

    const notification: Notification = {
      id: `n-${Date.now()}`,
      userId: booking.userId,
      type: "booking_rejected",
      title: "Booking Rejected",
      message: `Your booking for ${booking.resourceTitle} has been rejected.`,
      read: false,
      link: "/bookings",
      createdAt: new Date(),
    };
    setNotifications([notification, ...notifications]);

    toast.success("Booking rejected");
  };

  // Message handler
  const handleSendMessage = (bookingId: string, content: string) => {
    if (!currentUser) return;

    const booking = bookings.find((b) => b.id === bookingId);
    if (!booking) return;

    const resource = resources.find((r) => r.id === booking.resourceId);
    if (!resource) return;

    const receiverId = currentUser.id === resource.ownerId ? booking.userId : resource.ownerId;
    const receiverName = currentUser.id === resource.ownerId ? booking.userName : resource.ownerName;
    
    // Get profile images from users
    const receiver = users.find(u => u.id === receiverId);

    const newMessage: Message = {
      id: `m-${Date.now()}`,
      threadId: bookingId,
      senderId: currentUser.id,
      senderName: currentUser.name,
      senderProfileImage: currentUser.profileImage,
      receiverId,
      receiverName,
      receiverProfileImage: receiver?.profileImage,
      content,
      read: false,
      createdAt: new Date(),
    };

    setMessages([...messages, newMessage]);
    toast.success("Message sent");
  };

  // Message owner from resource details
  const handleMessageOwner = () => {
    if (!selectedResource) return;
    
    // Create a temporary booking context for the message
    // In a real app, you might create a booking first or have a general messaging system
    toast.info("Messaging feature - in a full implementation, this would open a message thread with the resource owner");
    setSelectedResource(null);
    setCurrentView("messages");
  };

  // Get user-specific data
  const userBookings = currentUser
    ? bookings.filter((b) => b.userId === currentUser.id)
    : [];
  const userNotifications = currentUser
    ? notifications.filter((n) => n.userId === currentUser.id)
    : [];
  const userMessages = currentUser
    ? messages.filter(
        (m) => m.senderId === currentUser.id || m.receiverId === currentUser.id
      )
    : [];

  const upcomingBookings = userBookings
    .filter(
      (b) =>
        b.startTime > new Date() &&
        (b.status === "approved" || b.status === "pending")
    )
    .sort((a, b) => a.startTime.getTime() - b.startTime.getTime());

  // If not logged in, show auth form
  if (!currentUser) {
    return (
      <>
        <AuthForm onLogin={handleLogin} onSignup={handleSignup} />
        <Toaster />
      </>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        user={currentUser}
        notifications={userNotifications}
        onLogout={handleLogout}
        onNavigate={handleNavigate}
        currentView={currentView}
        onSearchChange={setSearchQuery}
      />

      <div className="flex">
        <Navigation
          currentView={currentView}
          onNavigate={handleNavigate}
          user={currentUser}
        />

        <main className="flex-1 p-6 overflow-x-hidden">
          <div className="max-w-7xl mx-auto">
            {currentView === "dashboard" && (
              <DashboardView
                user={currentUser}
                upcomingBookings={upcomingBookings}
                recentResources={resources.filter((r) => r.status === "published")}
                onNavigate={handleNavigate}
                onViewResource={handleViewResourceDetails}
              />
            )}

            {currentView === "resources" && (
              <ResourcesView
                resources={resources}
                searchQuery={searchQuery}
                onViewDetails={handleViewResourceDetails}
              />
            )}

            {currentView === "bookings" && (
              <BookingsView
                bookings={userBookings}
                resources={resources}
                onCancelBooking={handleCancelBooking}
                onViewResource={(resourceId) => {
                  const resource = resources.find((r) => r.id === resourceId);
                  if (resource) handleViewResourceDetails(resource);
                }}
              />
            )}

            {currentView === "messages" && (
              <MessagesView
                messages={userMessages}
                bookings={userBookings}
                currentUser={currentUser}
                onSendMessage={handleSendMessage}
              />
            )}

            {currentView === "profile" && (
              <ProfileSettings
                user={currentUser}
                onUpdateProfile={handleUpdateProfile}
              />
            )}

            {currentView === "admin" && currentUser.role === "admin" && (
              <AdminView
                users={users}
                resources={resources}
                bookings={bookings}
                reviews={reviews}
                onApproveBooking={handleApproveBooking}
                onRejectBooking={handleRejectBooking}
                onDeleteResource={handleDeleteResource}
              />
            )}

            {currentView === "create-resource" &&
              (currentUser.role === "staff" || currentUser.role === "admin") && (
                <CreateResourceForm
                  currentUser={currentUser}
                  onSubmit={handleCreateResource}
                  onCancel={() => handleNavigate("dashboard")}
                />
              )}

            {currentView === "my-resources" &&
              (currentUser.role === "staff" || currentUser.role === "admin") && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h1 className="text-3xl mb-2">My Resources</h1>
                      <p className="text-gray-600">
                        Manage resources you own
                      </p>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {resources
                      .filter((r) => r.ownerId === currentUser.id)
                      .map((resource) => (
                        <div
                          key={resource.id}
                          className="border rounded-lg p-4 bg-white"
                        >
                          <h3 className="mb-2">{resource.title}</h3>
                          <p className="text-sm text-gray-600 mb-2">
                            {resource.bookingCount} bookings • {resource.reviewCount}{" "}
                            reviews
                          </p>
                          <div className="flex gap-2">
                            <button
                              className="text-sm text-blue-600 hover:underline"
                              onClick={() => handleViewResourceDetails(resource)}
                            >
                              View Details
                            </button>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
          </div>
        </main>
      </div>

      {selectedResource && (
        <ResourceDetailModal
          resource={selectedResource}
          reviews={reviews.filter((r) => r.resourceId === selectedResource.id)}
          currentUser={currentUser}
          onClose={handleCloseResourceDetails}
          onBook={handleBookResource}
          onMessageOwner={handleMessageOwner}
        />
      )}

      <Toaster />
    </div>
  );
}