import { useState } from "react";
import { Send, MessageSquare } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { ScrollArea } from "./ui/scroll-area";
import { Separator } from "./ui/separator";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { Message, Booking, User } from "../types";

interface MessagesViewProps {
  messages: Message[];
  bookings: Booking[];
  currentUser: User;
  onSendMessage: (bookingId: string, content: string) => void;
}

export function MessagesView({
  messages,
  bookings,
  currentUser,
  onSendMessage,
}: MessagesViewProps) {
  const [selectedBookingId, setSelectedBookingId] = useState<string | null>(null);
  const [messageContent, setMessageContent] = useState("");

  // Group messages by booking
  const messagesByBooking = messages.reduce((acc, message) => {
    if (!acc[message.threadId]) {
      acc[message.threadId] = [];
    }
    acc[message.threadId].push(message);
    return acc;
  }, {} as Record<string, Message[]>);

  // Get bookings with messages
  const bookingsWithMessages = bookings.filter(
    (b) => messagesByBooking[b.id] && messagesByBooking[b.id].length > 0
  );

  const handleSendMessage = () => {
    if (!selectedBookingId || !messageContent.trim()) return;
    onSendMessage(selectedBookingId, messageContent);
    setMessageContent("");
  };

  const selectedBooking = bookings.find((b) => b.id === selectedBookingId);
  const selectedMessages = selectedBookingId
    ? messagesByBooking[selectedBookingId] || []
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl mb-2">Messages</h1>
        <p className="text-gray-600">Communicate about your bookings</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Conversations List */}
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>Conversations</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {bookingsWithMessages.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                <MessageSquare className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                <p>No messages yet</p>
              </div>
            ) : (
              <ScrollArea className="h-[500px]">
                {bookingsWithMessages.map((booking) => {
                  const bookingMessages = messagesByBooking[booking.id];
                  const lastMessage = bookingMessages[bookingMessages.length - 1];
                  const hasUnread = bookingMessages.some(
                    (m) => !m.read && m.receiverId === currentUser.id
                  );

                  return (
                    <div key={booking.id}>
                      <button
                        className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
                          selectedBookingId === booking.id ? "bg-gray-100" : ""
                        }`}
                        onClick={() => setSelectedBookingId(booking.id)}
                      >
                        <div className="flex items-start justify-between mb-1">
                          <p className="line-clamp-1">{booking.resourceTitle}</p>
                          {hasUnread && (
                            <div className="h-2 w-2 bg-blue-600 rounded-full mt-1" />
                          )}
                        </div>
                        <p className="text-sm text-gray-600 line-clamp-1">
                          {lastMessage.content}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          {lastMessage.createdAt.toLocaleDateString()}
                        </p>
                      </button>
                      <Separator />
                    </div>
                  );
                })}
              </ScrollArea>
            )}
          </CardContent>
        </Card>

        {/* Messages Thread */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>
              {selectedBooking ? selectedBooking.resourceTitle : "Select a conversation"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!selectedBookingId ? (
              <div className="h-[500px] flex items-center justify-center text-gray-500">
                <div className="text-center">
                  <MessageSquare className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p>Select a conversation to view messages</p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <ScrollArea className="h-[400px] pr-4">
                  <div className="space-y-4">
                    {selectedMessages.map((message) => {
                      const isCurrentUser = message.senderId === currentUser.id;
                      return (
                        <div
                          key={message.id}
                          className={`flex gap-2 ${
                            isCurrentUser ? "justify-end" : "justify-start"
                          }`}
                        >
                          {!isCurrentUser && (
                            <Avatar className="h-8 w-8 flex-shrink-0">
                              <AvatarImage src={message.senderProfileImage} alt={message.senderName} />
                              <AvatarFallback>{message.senderName.charAt(0)}</AvatarFallback>
                            </Avatar>
                          )}
                          <div
                            className={`max-w-[70%] rounded-lg p-3 ${
                              isCurrentUser
                                ? "bg-blue-600 text-white"
                                : "bg-gray-100 text-gray-900"
                            }`}
                          >
                            <p className="text-xs opacity-80 mb-1">
                              {message.senderName}
                            </p>
                            <p className="text-sm">{message.content}</p>
                            <p className="text-xs opacity-70 mt-1">
                              {message.createdAt.toLocaleTimeString([], {
                                hour: "2-digit",
                                minute: "2-digit",
                              })}
                            </p>
                          </div>
                          {isCurrentUser && (
                            <Avatar className="h-8 w-8 flex-shrink-0">
                              <AvatarImage src={message.senderProfileImage} alt={message.senderName} />
                              <AvatarFallback>{message.senderName.charAt(0)}</AvatarFallback>
                            </Avatar>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </ScrollArea>

                <div className="flex gap-2">
                  <Textarea
                    placeholder="Type your message..."
                    value={messageContent}
                    onChange={(e) => setMessageContent(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    rows={2}
                  />
                  <Button onClick={handleSendMessage} disabled={!messageContent.trim()}>
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}