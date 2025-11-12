// Type definitions for the Campus Resource Hub

export type UserRole = "student" | "staff" | "admin";

export type ResourceStatus = "draft" | "published" | "archived";

export type BookingStatus = "pending" | "approved" | "rejected" | "completed" | "cancelled";

export type ResourceCategory = 
  | "study-room"
  | "lab-equipment"
  | "event-space"
  | "av-equipment"
  | "tutoring"
  | "other";

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  department?: string;
  profileImage?: string;
  createdAt: Date;
}

export interface Resource {
  id: string;
  title: string;
  description: string;
  images: string[];
  category: ResourceCategory;
  location: string;
  capacity: number;
  status: ResourceStatus;
  ownerId: string;
  ownerName: string;
  equipment?: string[];
  availabilityRules: string;
  requiresApproval: boolean;
  rating: number;
  reviewCount: number;
  bookingCount: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Booking {
  id: string;
  resourceId: string;
  resourceTitle: string;
  userId: string;
  userName: string;
  startTime: Date;
  endTime: Date;
  status: BookingStatus;
  notes?: string;
  recurrence?: "none" | "daily" | "weekly";
  createdAt: Date;
  updatedAt: Date;
}

export interface Review {
  id: string;
  resourceId: string;
  userId: string;
  userName: string;
  userProfileImage?: string;
  rating: number;
  comment: string;
  createdAt: Date;
}

export interface Message {
  id: string;
  threadId: string;
  senderId: string;
  senderName: string;
  senderProfileImage?: string;
  receiverId: string;
  receiverName: string;
  receiverProfileImage?: string;
  content: string;
  read: boolean;
  createdAt: Date;
}

export interface Notification {
  id: string;
  userId: string;
  type: "booking_confirmed" | "booking_pending" | "booking_approved" | "booking_rejected" | "new_message" | "review_received";
  title: string;
  message: string;
  read: boolean;
  link?: string;
  createdAt: Date;
}