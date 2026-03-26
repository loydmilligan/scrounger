import React, { useEffect, useState } from 'react';
import {
  Package,
  Users,
  DollarSign,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { api } from '@/utils/api';

interface Stats {
  total_sales: number;
  total_revenue: number;
  total_profit: number;
  average_sale: number;
  platform_breakdown: Record<string, { count: number; revenue: number }>;
  items: {
    total: number;
    listed: number;
    draft: number;
    sold: number;
  };
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentItems, setRecentItems] = useState<any[]>([]);
  const [recentLeads, setRecentLeads] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsData, itemsData, leadsData] = await Promise.all([
        api.getSalesStats(),
        api.getItems({ limit: '5' }),
        api.getLeads({ limit: '5' })
      ]);
      setStats(statsData);
      setRecentItems(itemsData.items || []);
      setRecentLeads(leadsData.leads || []);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);

  const statCards = [
    {
      title: 'Total Revenue',
      value: formatCurrency(stats?.total_revenue || 0),
      icon: DollarSign,
      color: 'from-green-500 to-emerald-600',
      change: '+12%',
      positive: true
    },
    {
      title: 'Total Profit',
      value: formatCurrency(stats?.total_profit || 0),
      icon: TrendingUp,
      color: 'from-blue-500 to-indigo-600',
      change: '+8%',
      positive: true
    },
    {
      title: 'Items Listed',
      value: stats?.items.listed || 0,
      icon: Package,
      color: 'from-purple-500 to-pink-600',
      change: String(stats?.items.draft || 0) + ' drafts',
      neutral: true
    },
    {
      title: 'Total Sales',
      value: stats?.total_sales || 0,
      icon: Users,
      color: 'from-amber-500 to-orange-600',
      change: `$${(stats?.average_sale || 0).toFixed(0)} avg`,
      neutral: true
    }
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'sold':
        return <Badge variant="success">Sold</Badge>;
      case 'listed':
        return <Badge variant="info">Listed</Badge>;
      case 'draft':
        return <Badge variant="secondary">Draft</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  const getLeadStatusBadge = (status: string) => {
    switch (status) {
      case 'new':
        return <Badge variant="info">New</Badge>;
      case 'contacted':
        return <Badge variant="warning">Contacted</Badge>;
      case 'negotiating':
        return <Badge variant="default">Negotiating</Badge>;
      case 'sold':
        return <Badge variant="success">Sold</Badge>;
      case 'dead':
        return <Badge variant="secondary">Dead</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
            Dashboard
          </h1>
          <p className="text-muted-foreground mt-1">
            Track your secondary sales performance
          </p>
        </div>
        <Button onClick={fetchData} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index} className="overflow-hidden">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </p>
                  <p className="text-2xl font-bold mt-2">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.color} shadow-lg`}>
                  <stat.icon className="h-5 w-5 text-white" />
                </div>
              </div>
              <div className="flex items-center mt-4 text-sm">
                {stat.positive && (
                  <ArrowUpRight className="h-4 w-4 text-green-500 mr-1" />
                )}
                {stat.positive === false && (
                  <ArrowDownRight className="h-4 w-4 text-red-500 mr-1" />
                )}
                <span className={stat.positive ? 'text-green-500' : stat.positive === false ? 'text-red-500' : 'text-muted-foreground'}>
                  {stat.change}
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Items */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Recent Items</CardTitle>
            <Button variant="ghost" size="sm" asChild>
              <a href="/items">View all</a>
            </Button>
          </CardHeader>
          <CardContent>
            {recentItems.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Package className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No items yet</p>
                <Button variant="link" asChild className="mt-2">
                  <a href="/items">Add your first item</a>
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {recentItems.map((item: any) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary/20 to-purple-500/20 flex items-center justify-center">
                        <Package className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium">{item.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {item.asking_price ? `$${item.asking_price}` : 'No price set'}
                        </p>
                      </div>
                    </div>
                    {getStatusBadge(item.status)}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Leads */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-lg">Recent Leads</CardTitle>
            <Button variant="ghost" size="sm" asChild>
              <a href="/leads">View all</a>
            </Button>
          </CardHeader>
          <CardContent>
            {recentLeads.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Users className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>No leads yet</p>
                <Button variant="link" asChild className="mt-2">
                  <a href="/leads">Import from Reddit</a>
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {recentLeads.map((lead: any) => (
                  <div
                    key={lead.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-white font-bold">
                        {lead.username[0].toUpperCase()}
                      </div>
                      <div>
                        <p className="font-medium">{lead.username}</p>
                        <p className="text-sm text-muted-foreground">
                          {lead.item_name || 'Unknown item'}
                        </p>
                      </div>
                    </div>
                    {getLeadStatusBadge(lead.status)}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Platform Breakdown */}
      {stats && Object.keys(stats.platform_breakdown).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Sales by Platform</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
              {Object.entries(stats.platform_breakdown).map(([platform, data]) => (
                <div
                  key={platform}
                  className="p-4 rounded-xl bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-900 text-center"
                >
                  <p className="font-semibold capitalize">{platform}</p>
                  <p className="text-2xl font-bold text-primary mt-1">
                    {data.count}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {formatCurrency(data.revenue)}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <Card className="bg-gradient-to-r from-primary/5 to-purple-500/5 border-primary/20">
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-primary/10">
                <AlertCircle className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="font-semibold">Quick Actions</p>
                <p className="text-sm text-muted-foreground">
                  Add items, import leads, or check prices with AI
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <Button asChild>
                <a href="/items">Add Item</a>
              </Button>
              <Button variant="outline" asChild>
                <a href="/ai">AI Assistant</a>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
