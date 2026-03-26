import React, { useEffect, useState } from 'react';
import {
  Plus,
  Search,
  Users,
  Edit,
  Trash2,
  RefreshCw,
  Link,
  MessageSquare,
  Clock
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
  DialogFooter,
  DialogDescription
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { api } from '@/utils/api';

const LEAD_STATUSES = ['new', 'contacted', 'negotiating', 'agreed', 'sold', 'dead'];
const PLATFORMS = ['reddit', 'ebay', 'offerup', 'swappa', 'other'];

export default function Leads() {
  const [leads, setLeads] = useState<any[]>([]);
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [redditDialogOpen, setRedditDialogOpen] = useState(false);
  const [editingLead, setEditingLead] = useState<any>(null);

  const [formData, setFormData] = useState({
    item_id: '',
    username: '',
    platform: 'reddit',
    contact_method: 'reddit_dm',
    contact_info: '',
    status: 'new',
    offered_price: '',
    notes: ''
  });

  const [redditUrl, setRedditUrl] = useState('');
  const [redditItemId, setRedditItemId] = useState('');
  const [importing, setImporting] = useState(false);

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (statusFilter) params.status = statusFilter;
      const data = await api.getLeads(params);
      setLeads(data.leads || []);
    } catch (error) {
      console.error('Failed to fetch leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchItems = async () => {
    try {
      const data = await api.getItems({ status: 'listed' });
      setItems(data.items || []);
    } catch (error) {
      console.error('Failed to fetch items:', error);
    }
  };

  useEffect(() => {
    fetchLeads();
    fetchItems();
  }, [statusFilter]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        item_id: parseInt(formData.item_id)
      };

      if (editingLead) {
        await api.updateLead(editingLead.id, submitData);
      } else {
        await api.createLead(submitData);
      }
      setDialogOpen(false);
      resetForm();
      fetchLeads();
    } catch (error) {
      console.error('Failed to save lead:', error);
    }
  };

  const handleRedditImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!redditUrl || !redditItemId) return;

    setImporting(true);
    try {
      const result = await api.importRedditLeads({
        url: redditUrl,
        item_id: parseInt(redditItemId)
      });
      alert(`Imported ${result.created} leads! (${result.skipped} duplicates skipped)`);
      setRedditDialogOpen(false);
      setRedditUrl('');
      setRedditItemId('');
      fetchLeads();
    } catch (error: any) {
      alert(error.message || 'Failed to import leads');
    } finally {
      setImporting(false);
    }
  };

  const handleEdit = (lead: any) => {
    setEditingLead(lead);
    setFormData({
      item_id: lead.item_id.toString(),
      username: lead.username || '',
      platform: lead.platform || 'reddit',
      contact_method: lead.contact_method || 'reddit_dm',
      contact_info: lead.contact_info || '',
      status: lead.status || 'new',
      offered_price: lead.offered_price || '',
      notes: lead.notes || ''
    });
    setDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this lead?')) return;
    try {
      await api.deleteLead(id);
      fetchLeads();
    } catch (error) {
      console.error('Failed to delete lead:', error);
    }
  };

  const handleStatusChange = async (leadId: number, newStatus: string) => {
    try {
      await api.updateLead(leadId, { status: newStatus });
      fetchLeads();
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  const resetForm = () => {
    setEditingLead(null);
    setFormData({
      item_id: '',
      username: '',
      platform: 'reddit',
      contact_method: 'reddit_dm',
      contact_info: '',
      status: 'new',
      offered_price: '',
      notes: ''
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'new':
        return <Badge variant="info">New</Badge>;
      case 'contacted':
        return <Badge variant="warning">Contacted</Badge>;
      case 'negotiating':
        return <Badge variant="default">Negotiating</Badge>;
      case 'agreed':
        return <Badge className="bg-cyan-500">Agreed</Badge>;
      case 'sold':
        return <Badge variant="success">Sold</Badge>;
      case 'dead':
        return <Badge variant="secondary">Dead</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const getTimeSince = (date: string) => {
    const diff = Date.now() - new Date(date).getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Leads</h1>
          <p className="text-muted-foreground mt-1">
            Track potential buyers and conversations
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setRedditDialogOpen(true)}>
            <Link className="h-4 w-4 mr-2" />
            Import from Reddit
          </Button>
          <Button onClick={() => { resetForm(); setDialogOpen(true); }}>
            <Plus className="h-4 w-4 mr-2" />
            Add Lead
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <Select value={statusFilter || 'all'} onValueChange={(v) => setStatusFilter(v === 'all' ? '' : v)}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                {LEAD_STATUSES.map(status => (
                  <SelectItem key={status} value={status} className="capitalize">
                    {status}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <div className="flex-1" />
            <Button variant="outline" onClick={fetchLeads}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Leads List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : leads.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Users className="h-16 w-16 mx-auto mb-4 text-muted-foreground/50" />
            <h3 className="text-lg font-semibold">No leads yet</h3>
            <p className="text-muted-foreground mt-1">
              Import leads from Reddit or add them manually
            </p>
            <div className="flex gap-2 justify-center mt-4">
              <Button variant="outline" onClick={() => setRedditDialogOpen(true)}>
                <Link className="h-4 w-4 mr-2" />
                Import from Reddit
              </Button>
              <Button onClick={() => { resetForm(); setDialogOpen(true); }}>
                <Plus className="h-4 w-4 mr-2" />
                Add Lead
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {leads.map((lead) => (
            <Card key={lead.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-4">
                <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                  <div className="flex items-center gap-3 flex-1">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center text-white font-bold text-lg">
                      {lead.username[0].toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">{lead.username}</span>
                        {getStatusBadge(lead.status)}
                      </div>
                      <p className="text-sm text-muted-foreground truncate">
                        {lead.item_name || 'Unknown item'}
                      </p>
                      <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                        <span className="capitalize">{lead.platform}</span>
                        {lead.offered_price && (
                          <span className="font-medium text-primary">
                            Offered: {lead.offered_price}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {getTimeSince(lead.updated_at)}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Select
                      value={lead.status}
                      onValueChange={(value) => handleStatusChange(lead.id, value)}
                    >
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {LEAD_STATUSES.map(status => (
                          <SelectItem key={status} value={status} className="capitalize">
                            {status}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button variant="outline" size="icon" onClick={() => handleEdit(lead)}>
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="icon" onClick={() => handleDelete(lead.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                {lead.notes && (
                  <div className="mt-3 p-3 bg-muted rounded-lg text-sm">
                    <MessageSquare className="h-4 w-4 inline mr-2 text-muted-foreground" />
                    {lead.notes}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add/Edit Lead Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>
              {editingLead ? 'Edit Lead' : 'Add New Lead'}
            </DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Item *</label>
              <Select
                value={formData.item_id}
                onValueChange={(value) => setFormData({ ...formData, item_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select an item" />
                </SelectTrigger>
                <SelectContent>
                  {items.map(item => (
                    <SelectItem key={item.id} value={item.id.toString()}>
                      {item.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-sm font-medium">Username *</label>
              <Input
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                placeholder="Reddit username, eBay ID, etc."
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Platform</label>
                <Select
                  value={formData.platform}
                  onValueChange={(value) => setFormData({ ...formData, platform: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {PLATFORMS.map(platform => (
                      <SelectItem key={platform} value={platform} className="capitalize">
                        {platform}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
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
                    {LEAD_STATUSES.map(status => (
                      <SelectItem key={status} value={status} className="capitalize">
                        {status}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium">Offered Price</label>
              <Input
                value={formData.offered_price}
                onChange={(e) => setFormData({ ...formData, offered_price: e.target.value })}
                placeholder="e.g., $150 or 'asking'"
              />
            </div>

            <div>
              <label className="text-sm font-medium">Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                placeholder="Notes about this lead..."
                className="w-full min-h-[80px] px-3 py-2 rounded-md border bg-background text-sm"
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">
                {editingLead ? 'Save Changes' : 'Add Lead'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Reddit Import Dialog */}
      <Dialog open={redditDialogOpen} onOpenChange={setRedditDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Import Leads from Reddit</DialogTitle>
            <DialogDescription>
              Paste a Reddit post URL to automatically import all commenters as potential leads.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleRedditImport} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Reddit Post URL *</label>
              <Input
                value={redditUrl}
                onChange={(e) => setRedditUrl(e.target.value)}
                placeholder="https://www.reddit.com/r/hardwareswap/comments/..."
                required
              />
              <p className="text-xs text-muted-foreground mt-1">
                Paste the full URL of your sales post
              </p>
            </div>

            <div>
              <label className="text-sm font-medium">Associate with Item *</label>
              <Select value={redditItemId} onValueChange={setRedditItemId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select an item" />
                </SelectTrigger>
                <SelectContent>
                  {items.map(item => (
                    <SelectItem key={item.id} value={item.id.toString()}>
                      {item.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setRedditDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={importing || !redditUrl || !redditItemId}>
                {importing ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Importing...
                  </>
                ) : (
                  <>
                    <Link className="h-4 w-4 mr-2" />
                    Import Leads
                  </>
                )}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
