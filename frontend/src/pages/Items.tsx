import React, { useEffect, useState } from 'react';
import {
  Plus,
  Search,
  Package,
  Edit,
  Trash2,
  RefreshCw,
  Filter,
  MoreVertical
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { api } from '@/utils/api';

const PLATFORMS = ['reddit', 'ebay', 'offerup', 'swappa', 'facebook'];
const CONDITIONS = ['new', 'like_new', 'good', 'fair', 'poor'];
const STATUSES = ['draft', 'listed', 'sold', 'archived'];

export default function Items() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: '',
    condition: 'good',
    asking_price: '',
    min_price: '',
    cost_basis: '',
    status: 'draft',
    platforms: [] as string[],
    notes: ''
  });

  const fetchItems = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (search) params.search = search;
      if (statusFilter) params.status = statusFilter;
      const data = await api.getItems(params);
      setItems(data.items || []);
    } catch (error) {
      console.error('Failed to fetch items:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, [statusFilter]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchItems();
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        asking_price: formData.asking_price ? parseFloat(formData.asking_price) : null,
        min_price: formData.min_price ? parseFloat(formData.min_price) : null,
        cost_basis: formData.cost_basis ? parseFloat(formData.cost_basis) : null
      };

      if (editingItem) {
        await api.updateItem(editingItem.id, submitData);
      } else {
        await api.createItem(submitData);
      }
      setDialogOpen(false);
      resetForm();
      fetchItems();
    } catch (error) {
      console.error('Failed to save item:', error);
    }
  };

  const handleEdit = (item: any) => {
    setEditingItem(item);
    setFormData({
      name: item.name || '',
      description: item.description || '',
      category: item.category || '',
      condition: item.condition || 'good',
      asking_price: item.asking_price?.toString() || '',
      min_price: item.min_price?.toString() || '',
      cost_basis: item.cost_basis?.toString() || '',
      status: item.status || 'draft',
      platforms: item.platforms || [],
      notes: item.notes || ''
    });
    setDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this item?')) return;
    try {
      await api.deleteItem(id);
      fetchItems();
    } catch (error) {
      console.error('Failed to delete item:', error);
    }
  };

  const resetForm = () => {
    setEditingItem(null);
    setFormData({
      name: '',
      description: '',
      category: '',
      condition: 'good',
      asking_price: '',
      min_price: '',
      cost_basis: '',
      status: 'draft',
      platforms: [],
      notes: ''
    });
  };

  const openNewDialog = () => {
    resetForm();
    setDialogOpen(true);
  };

  const togglePlatform = (platform: string) => {
    setFormData(prev => ({
      ...prev,
      platforms: prev.platforms.includes(platform)
        ? prev.platforms.filter(p => p !== platform)
        : [...prev.platforms, platform]
    }));
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'sold':
        return <Badge variant="success">Sold</Badge>;
      case 'listed':
        return <Badge variant="info">Listed</Badge>;
      case 'draft':
        return <Badge variant="secondary">Draft</Badge>;
      case 'archived':
        return <Badge variant="outline">Archived</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Items</h1>
          <p className="text-muted-foreground mt-1">
            Manage your inventory of items for sale
          </p>
        </div>
        <Button onClick={openNewDialog}>
          <Plus className="h-4 w-4 mr-2" />
          Add Item
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search items..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter || 'all'} onValueChange={(v) => setStatusFilter(v === 'all' ? '' : v)}>
              <SelectTrigger className="w-full sm:w-40">
                <SelectValue placeholder="All Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                {STATUSES.map(status => (
                  <SelectItem key={status} value={status} className="capitalize">
                    {status.replace('_', ' ')}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={fetchItems}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Items List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : items.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Package className="h-16 w-16 mx-auto mb-4 text-muted-foreground/50" />
            <h3 className="text-lg font-semibold">No items yet</h3>
            <p className="text-muted-foreground mt-1">
              Start by adding your first item to sell
            </p>
            <Button className="mt-4" onClick={openNewDialog}>
              <Plus className="h-4 w-4 mr-2" />
              Add Item
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((item) => (
            <Card key={item.id} className="hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg line-clamp-1">{item.name}</CardTitle>
                    <p className="text-sm text-muted-foreground mt-1">
                      {item.category || 'Uncategorized'}
                    </p>
                  </div>
                  {getStatusBadge(item.status)}
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
                  {item.description || 'No description'}
                </p>

                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-2xl font-bold text-primary">
                      {item.asking_price ? `$${item.asking_price}` : 'No price'}
                    </p>
                    {item.cost_basis && (
                      <p className="text-xs text-muted-foreground">
                        Cost: ${item.cost_basis}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{item.lead_count || 0} leads</p>
                    <p className="text-xs text-muted-foreground capitalize">
                      {item.condition?.replace('_', ' ') || 'Unknown'}
                    </p>
                  </div>
                </div>

                {item.platforms?.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-4">
                    {item.platforms.map((platform: string) => (
                      <Badge key={platform} variant="outline" className="text-xs capitalize">
                        {platform}
                      </Badge>
                    ))}
                  </div>
                )}

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() => handleEdit(item)}
                  >
                    <Edit className="h-4 w-4 mr-1" />
                    Edit
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(item.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add/Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingItem ? 'Edit Item' : 'Add New Item'}
            </DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2">
                <label className="text-sm font-medium">Name *</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., NVIDIA RTX 3080"
                  required
                />
              </div>

              <div className="sm:col-span-2">
                <label className="text-sm font-medium">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Describe the item..."
                  className="w-full min-h-[100px] px-3 py-2 rounded-md border bg-background text-sm"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Category</label>
                <Input
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  placeholder="e.g., Graphics Card"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Condition</label>
                <Select
                  value={formData.condition}
                  onValueChange={(value) => setFormData({ ...formData, condition: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {CONDITIONS.map(condition => (
                      <SelectItem key={condition} value={condition} className="capitalize">
                        {condition.replace('_', ' ')}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">Asking Price ($)</label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.asking_price}
                  onChange={(e) => setFormData({ ...formData, asking_price: e.target.value })}
                  placeholder="0.00"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Minimum Price ($)</label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.min_price}
                  onChange={(e) => setFormData({ ...formData, min_price: e.target.value })}
                  placeholder="0.00"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Cost Basis ($)</label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.cost_basis}
                  onChange={(e) => setFormData({ ...formData, cost_basis: e.target.value })}
                  placeholder="What you paid"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Status</label>
                <Select
                  value={formData.status}
                  onValueChange={(value) => setFormData({ ...formData, status: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {STATUSES.map(status => (
                      <SelectItem key={status} value={status} className="capitalize">
                        {status.replace('_', ' ')}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="sm:col-span-2">
                <label className="text-sm font-medium">Platforms</label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {PLATFORMS.map(platform => (
                    <Button
                      key={platform}
                      type="button"
                      variant={formData.platforms.includes(platform) ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => togglePlatform(platform)}
                      className="capitalize"
                    >
                      {platform}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="sm:col-span-2">
                <label className="text-sm font-medium">Notes</label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Internal notes..."
                  className="w-full min-h-[80px] px-3 py-2 rounded-md border bg-background text-sm"
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">
                {editingItem ? 'Save Changes' : 'Add Item'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
