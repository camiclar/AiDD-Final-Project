import { Home, Search, Calendar, MessageSquare, Settings, Shield, Plus } from "lucide-react";
import { Button } from "./ui/button";
import { User } from "../types";

interface NavigationProps {
  currentView: string;
  onNavigate: (view: string) => void;
  user: User;
}

export function Navigation({ currentView, onNavigate, user }: NavigationProps) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: Home },
    { id: "resources", label: "Browse Resources", icon: Search },
    { id: "bookings", label: "My Bookings", icon: Calendar },
    { id: "messages", label: "Messages", icon: MessageSquare },
  ];

  if (user.role === "staff" || user.role === "admin") {
    navItems.push({ id: "my-resources", label: "My Resources", icon: Settings });
  }

  if (user.role === "admin") {
    navItems.push({ id: "admin", label: "Admin Panel", icon: Shield });
  }

  return (
    <nav className="bg-white border-r min-h-[calc(100vh-4rem)] w-64 p-4 hidden md:block">
      <div className="space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <Button
              key={item.id}
              variant={currentView === item.id ? "secondary" : "ghost"}
              className="w-full justify-start"
              onClick={() => onNavigate(item.id)}
            >
              <Icon className="mr-2 h-4 w-4" />
              {item.label}
            </Button>
          );
        })}
      </div>

      {(user.role === "staff" || user.role === "admin") && (
        <div className="mt-6 pt-6 border-t">
          <Button
            className="w-full"
            onClick={() => onNavigate("create-resource")}
          >
            <Plus className="mr-2 h-4 w-4" />
            Create Resource
          </Button>
        </div>
      )}
    </nav>
  );
}
