import { useState } from "react";
import { ArrowLeft, Upload, X } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Textarea } from "./ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Switch } from "./ui/switch";
import { ResourceCategory, User } from "../types";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface CreateResourceFormProps {
  currentUser: User;
  onSubmit: (resourceData: any) => void;
  onCancel: () => void;
}

export function CreateResourceForm({
  currentUser,
  onSubmit,
  onCancel,
}: CreateResourceFormProps) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category: "study-room" as ResourceCategory,
    location: "",
    capacity: 1,
    availabilityRules: "",
    requiresApproval: false,
    equipment: "",
    imageUrl: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const equipmentList = formData.equipment
      .split(",")
      .map((item) => item.trim())
      .filter((item) => item.length > 0);

    onSubmit({
      ...formData,
      equipment: equipmentList,
      ownerId: currentUser.id,
      ownerName: currentUser.name,
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={onCancel}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl">Create New Resource</h1>
          <p className="text-gray-600">Add a new resource for campus use</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Resource Details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="title">Resource Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) =>
                  setFormData({ ...formData, title: e.target.value })
                }
                placeholder="e.g., Library Study Room A"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description *</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="Describe the resource, its features, and any requirements..."
                rows={4}
                required
              />
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="category">Category *</Label>
                <Select
                  value={formData.category}
                  onValueChange={(value: ResourceCategory) =>
                    setFormData({ ...formData, category: value })
                  }
                >
                  <SelectTrigger id="category">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="study-room">Study Room</SelectItem>
                    <SelectItem value="lab-equipment">Lab Equipment</SelectItem>
                    <SelectItem value="event-space">Event Space</SelectItem>
                    <SelectItem value="av-equipment">AV Equipment</SelectItem>
                    <SelectItem value="tutoring">Tutoring</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="capacity">Capacity *</Label>
                <Input
                  id="capacity"
                  type="number"
                  min="1"
                  value={formData.capacity}
                  onChange={(e) =>
                    setFormData({ ...formData, capacity: parseInt(e.target.value) })
                  }
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="location">Location *</Label>
              <Input
                id="location"
                value={formData.location}
                onChange={(e) =>
                  setFormData({ ...formData, location: e.target.value })
                }
                placeholder="e.g., Library Building, 3rd Floor, Room 301"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="availability">Availability Rules *</Label>
              <Input
                id="availability"
                value={formData.availabilityRules}
                onChange={(e) =>
                  setFormData({ ...formData, availabilityRules: e.target.value })
                }
                placeholder="e.g., Mon-Fri 8AM-10PM, Sat-Sun 10AM-6PM"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="equipment">Equipment & Amenities (Optional)</Label>
              <Input
                id="equipment"
                value={formData.equipment}
                onChange={(e) =>
                  setFormData({ ...formData, equipment: e.target.value })
                }
                placeholder="Separate items with commas (e.g., Whiteboard, Projector, WiFi)"
              />
              <p className="text-sm text-gray-500">
                Separate each item with a comma
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="imageUrl">Resource Image (Optional)</Label>
              <div className="space-y-3">
                {formData.imageUrl && (
                  <div className="relative w-full aspect-video rounded-lg overflow-hidden bg-gray-100">
                    <ImageWithFallback
                      src={formData.imageUrl}
                      alt="Resource preview"
                      className="w-full h-full object-cover"
                    />
                    <Button
                      type="button"
                      variant="destructive"
                      size="icon"
                      className="absolute top-2 right-2"
                      onClick={() => setFormData({ ...formData, imageUrl: "" })}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                )}
                <Input
                  id="imageUrl"
                  value={formData.imageUrl}
                  onChange={(e) =>
                    setFormData({ ...formData, imageUrl: e.target.value })
                  }
                  placeholder="Enter image URL from Unsplash, Pexels, etc."
                />
                <p className="text-sm text-gray-500">
                  Add an image URL to showcase your resource. Leave blank to use a default image.
                </p>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div className="space-y-0.5">
                <Label htmlFor="approval">Require Approval</Label>
                <p className="text-sm text-gray-500">
                  Bookings will need your approval before confirmation
                </p>
              </div>
              <Switch
                id="approval"
                checked={formData.requiresApproval}
                onCheckedChange={(checked) =>
                  setFormData({ ...formData, requiresApproval: checked })
                }
              />
            </div>

            <div className="flex gap-3 pt-4">
              <Button type="button" variant="outline" onClick={onCancel} className="flex-1">
                Cancel
              </Button>
              <Button type="submit" className="flex-1">
                Create Resource
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}