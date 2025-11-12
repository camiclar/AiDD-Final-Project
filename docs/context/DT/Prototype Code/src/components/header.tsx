import { Bell, LogOut, Menu, Search, User } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Badge } from "./ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar";
import { User as UserType, Notification } from "../types";

interface HeaderProps {
  user: UserType;
  notifications: Notification[];
  onLogout: () => void;
  onNavigate: (view: string) => void;
  onSearchChange?: (query: string) => void;
  currentView: string;
}

export function Header({ user, notifications, onLogout, onNavigate, onSearchChange, currentView }: HeaderProps) {
  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <header className="border-b bg-white sticky top-0 z-50">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => onNavigate("menu")}
            >
              <Menu className="h-5 w-5" />
            </Button>
            <div className="cursor-pointer" onClick={() => onNavigate("dashboard")}>
              <h1 className="text-xl">Campus Resource Hub</h1>
            </div>
          </div>

          {currentView === "resources" && onSearchChange && (
            <div className="hidden md:flex flex-1 max-w-md">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search resources..."
                  className="pl-10"
                  onChange={(e) => onSearchChange(e.target.value)}
                />
              </div>
            </div>
          )}

          <div className="flex items-center gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="relative">
                  <Bell className="h-5 w-5" />
                  {unreadCount > 0 && (
                    <Badge
                      variant="destructive"
                      className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
                    >
                      {unreadCount}
                    </Badge>
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-80">
                <DropdownMenuLabel>Notifications</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {notifications.length === 0 ? (
                  <div className="p-4 text-sm text-gray-500 text-center">
                    No notifications
                  </div>
                ) : (
                  <div className="max-h-96 overflow-y-auto">
                    {notifications.slice(0, 5).map((notification) => (
                      <DropdownMenuItem
                        key={notification.id}
                        className="flex flex-col items-start p-3 cursor-pointer"
                        onClick={() => notification.link && onNavigate(notification.link)}
                      >
                        <div className="flex items-start justify-between w-full">
                          <span className="font-medium">{notification.title}</span>
                          {!notification.read && (
                            <div className="h-2 w-2 bg-blue-600 rounded-full mt-1" />
                          )}
                        </div>
                        <span className="text-sm text-gray-600 mt-1">
                          {notification.message}
                        </span>
                        <span className="text-xs text-gray-400 mt-1">
                          {notification.createdAt.toLocaleDateString()}
                        </span>
                      </DropdownMenuItem>
                    ))}
                  </div>
                )}
                {notifications.length > 0 && (
                  <>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      className="text-center justify-center text-blue-600"
                      onClick={() => onNavigate("notifications")}
                    >
                      View all notifications
                    </DropdownMenuItem>
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="relative h-10 w-10 rounded-full overflow-hidden border-2 border-transparent hover:border-gray-200 transition-colors focus:outline-none focus:border-blue-500">
                  <Avatar className="h-full w-full">
                    <AvatarImage src={user.profileImage} />
                    <AvatarFallback>
                      {user.name.split(" ").map((n) => n[0]).join("")}
                    </AvatarFallback>
                  </Avatar>
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>
                  <div className="flex flex-col">
                    <span>{user.name}</span>
                    <span className="text-xs text-gray-500 capitalize">{user.role}</span>
                    {user.department && (
                      <span className="text-xs text-gray-500">{user.department}</span>
                    )}
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => onNavigate("profile")}>
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => onNavigate("bookings")}>
                  My Bookings
                </DropdownMenuItem>
                {user.role === "admin" && (
                  <DropdownMenuItem onClick={() => onNavigate("admin")}>
                    Admin Panel
                  </DropdownMenuItem>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={onLogout}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </header>
  );
}