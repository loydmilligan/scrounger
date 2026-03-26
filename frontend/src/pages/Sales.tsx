import React, { useEffect, useState } from 'react';
import {
  Plus,
  DollarSign,
  TrendingUp,
  Package,
  RefreshCw,
  Edit,
  Trash2,
  Truck
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

const PLATFORMS = ['reddit', 'ebay', 'offerup', 'swappa', 'facebook', 'other'];
const CARRIERS = ['usps', 'ups', 'fedex', 'other'];

export default function Sales() {
  const [sales, setSales] = useState<any[]>([]);
  const [items, setItems] = useState<any[]>([]);
  const [leads, setLeads] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingSale, setEditingSale] = useState<any>(null);

  const [formData, setFormData] = useState({
    item_id: '',
    lead_id: '',
    sale_price: '',
    platform: '',
    buyer_username: '',
    shipping_cost: '',
    shipping_carrier: '',
    tracking_number: '',
    platform_fees: '',
    payment_fees: '',
    notes: ''
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [salesData, itemsData, leadsData, statsData] = await Promise.all([
        api.getSales({}),
        api.getItems({ status: 'listed' }),
        api.getLeads({ status: 'agreed' }),
        api.getSalesStats()
      ]);
      setSales(salesData.sales || []);
      setItems(itemsData.items || []);
      setLeads(leadsData.leads || []);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = {
        item_id: parseInt(formData.item_id),
        lead_id: formData.lead_id ? parseInt(formData.lead_id) : null,
        sale_price: parseFloat(formData.sale_price),
        platform: formData.platform || null,
        buyer_username: formData.buyer_username || null,
        shipping_cost: formData.shipping_cost ? parseFloat(formData.shipping_cost) : 0,
        shipping_carrier: formData.shipping_carrier || null,
        tracking_number: formData.tracking_number || null,
        platform_fees: formData.platform_fees ? parseFloat(formData.platform_fees) : 0,
        payment_fees: formData.payment_fees ? parseFloat(formData.payment_fees) : 0,
        notes: formData.notes || null
      };

      if (editingSale) {
        await api.updateSale(editingSale.id, submitData);
      } else {
        await api.createSale(submitData);
      }
      setDialogOpen(false);
      resetForm();
      fetchData();
    } catch (error: any) {
      alert(error.message || 'Failed to save sale');
    }
  };

  const handleEdit = (sale: any) => {
    setEditingSale(sale);
    setFormData({
      item_id: sale.item_id.toString(),
      lead_id: sale.lead_id?.toString() || '',
      sale_price: sale.sale_price.toString(),
      platform: sale.platform || '',
      buyer_username: sale.buyer_username || '',
      shipping_cost: sale.shipping_cost?.toString() || '',
      shipping_carrier: sale.shipping_carrier || '',
      tracking_number: sale.tracking_number || '',
      platform_fees: sale.platform_fees?.toString() || '',
      payment_fees: sale.payment_fees?.toString() || '',
      notes: sale.notes || ''
    });
    setDialogOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this sale? The item will be marked as listed again.')) return;
    try {
      await api.deleteSale(id);
      fetchData();
    } catch (error) {
      console.error('Failed to delete sale:', error);
    }
  };

  const resetForm = () => {
    setEditingSale(null);
    setFormData({
      item_id: '',
      lead_id: '',
      sale_price: '',
      platform: '',
      buyer_username: '',
      shipping_cost: '',
      shipping_carrier: '',
      tracking_number: '',
      platform_fees: '',
      payment_fees: '',
      notes: ''
    });
  };

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);

  const formatDate = (date: string) =>
    new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Sales</h1>
          <p className="text-muted-foreground mt-1">
            Track completed sales and profits
          </p>
        </div>
        <Button onClick={() => { resetForm(); setDialogOpen(true); }}>
          <Plus className="h-4 w-4 mr-2" />
          Record Sale
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Revenue</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrency(stats?.total_revenue || 0)}
                </p>
              </div>
              <div className="p-3 rounded-xl bg-green-500/20">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border-blue-500/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Profit</p>
                <p className="text-2xl font-bold text-blue-600">
                  {formatCurrency(stats?.total_profit || 0)}
                </p>
              </div>
              <div className="p-3 rounded-xl bg-blue-500/20">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Items Sold</p>
                <p className="text-2xl font-bold text-purple-600">
                  {stats?.total_sales || 0}
                </p>
              </div>
              <div className="p-3 rounded-xl bg-purple-500/20">
                <Package className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sales List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : sales.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <DollarSign className="h-16 w-16 mx-auto mb-4 text-muted-foreground/50" />
            <h3 className="text-lg font-semibold">No sales yet</h3>
            <p className="text-muted-foreground mt-1">
              Record your first sale when you close a deal
            </p>
            <Button className="mt-4" onClick={() => { resetForm(); setDialogOpen(true); }}>
              <Plus className="h-4 w-4 mr-2" />
              Record Sale
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {sales.map((sale) => (
            <Card key={sale.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-4">
                <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                  <div className="flex items-center gap-3 flex-1">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center text-white">
                      <DollarSign className="h-6 w-6" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">{sale.item_name || 'Unknown item'}</span>
                        <Badge variant="success">Sold</Badge>
                      </div>
                      <div className="flex items-center gap-3 text-sm text-muted-foreground mt-1">
                        {sale.buyer_username && <span>to {sale.buyer_username}</span>}
                        {sale.platform && <span className="capitalize">{sale.platform}</span>}
                        <span>{formatDate(sale.sale_date)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-xl font-bold text-green-600">
                        {formatCurrency(sale.sale_price)}
                      </p>
                      {sale.profit !== null && (
                        <p className={`text-sm ${sale.profit >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                          Profit: {formatCurrency(sale.profit)}
                        </p>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {sale.tracking_number && (
                        <Badge variant="outline" className="flex items-center gap-1">
                          <Truck className="h-3 w-3" />
                          Shipped
                        </Badge>
                      )}
                      <Button variant="outline" size="icon" onClick={() => handleEdit(sale)}>
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="icon" onClick={() => handleDelete(sale.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>

                {(sale.shipping_cost > 0 || sale.platform_fees > 0) && (
                  <div className="flex gap-4 mt-3 text-sm text-muted-foreground">
                    {sale.shipping_cost > 0 && (
                      <span>Shipping: {formatCurrency(sale.shipping_cost)}</span>
                    )}
                    {sale.platform_fees > 0 && (
                      <span>Fees: {formatCurrency(sale.platform_fees + (sale.payment_fees || 0))}</span>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add/Edit Sale Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingSale ? 'Edit Sale' : 'Record New Sale'}
            </DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Item *</label>
              <Select
                value={formData.item_id}
                onValueChange={(value) => setFormData({ ...formData, item_id: value })}
                disabled={!!editingSale}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select an item" />
                </SelectTrigger>
                <SelectContent>
                  {items.map(item => (
                    <SelectItem key={item.id} value={item.id.toString()}>
                      {item.name} - ${item.asking_price || 0}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Sale Price *</label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.sale_price}
                  onChange={(e) => setFormData({ ...formData, sale_price: e.target.value })}
                  placeholder="0.00"
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium">Platform</label>
                <Select
                  value={formData.platform}
                  onValueChange={(value) => setFormData({ ...formData, platform: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select platform" />
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
            </div>

            <div>
              <label className="text-sm font-medium">Buyer Username</label>
              <Input
                value={formData.buyer_username}
                onChange={(e) => setFormData({ ...formData, buyer_username: e.target.value })}
                placeholder="Reddit username, eBay ID, etc."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Shipping Cost</label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.shipping_cost}
                  onChange={(e) => setFormData({ ...formData, shipping_cost: e.target.value })}
                  placeholder="0.00"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Carrier</label>
                <Select
                  value={formData.shipping_carrier}
                  onValueChange={(value) => setFormData({ ...formData, shipping_carrier: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select carrier" />
                  </SelectTrigger>
                  <SelectContent>
                    {CARRIERS.map(carrier => (
                      <SelectItem key={carrier} value={carrier} className="uppercase">
                        {carrier}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium">Tracking Number</label>
              <Input
                value={formData.tracking_number}
                onChange={(e) => setFormData({ ...formData, tracking_number: e.target.value })}
                placeholder="Tracking number"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Platform Fees</label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.platform_fees}
                  onChange={(e) => setFormData({ ...formData, platform_fees: e.target.value })}
                  placeholder="0.00"
                />
              </div>

              <div>
                <label className="text-sm font-medium">Payment Fees</label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.payment_fees}
                  onChange={(e) => setFormData({ ...formData, payment_fees: e.target.value })}
                  placeholder="PayPal, etc."
                />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium">Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                placeholder="Notes about this sale..."
                className="w-full min-h-[80px] px-3 py-2 rounded-md border bg-background text-sm"
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">
                {editingSale ? 'Save Changes' : 'Record Sale'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
