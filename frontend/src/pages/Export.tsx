import React, { useState } from 'react';
import {
  Download,
  Upload,
  FileSpreadsheet,
  Calendar,
  CheckSquare,
  RefreshCw,
  FileText,
  AlertCircle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { api } from '@/utils/api';

export default function ExportPage() {
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<any>(null);

  const handleDownload = (url: string, filename: string) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleImportCSV = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setImporting(true);
    setImportResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/export/items/csv', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Import failed');
      }

      const result = await response.json();
      setImportResult(result);
    } catch (error: any) {
      setImportResult({ success: false, errors: [error.message] });
    } finally {
      setImporting(false);
      e.target.value = '';
    }
  };

  const exportOptions = [
    {
      title: 'Items CSV',
      description: 'Export all your inventory items to a spreadsheet',
      icon: FileSpreadsheet,
      color: 'from-blue-500 to-indigo-600',
      action: () => handleDownload(api.exportItemsCSV(), 'items.csv')
    },
    {
      title: 'Leads CSV',
      description: 'Export all leads and potential buyers',
      icon: FileSpreadsheet,
      color: 'from-green-500 to-emerald-600',
      action: () => handleDownload(api.exportLeadsCSV(), 'leads.csv')
    },
    {
      title: 'Sales CSV',
      description: 'Export your complete sales history',
      icon: FileSpreadsheet,
      color: 'from-purple-500 to-pink-600',
      action: () => handleDownload(api.exportSalesCSV(), 'sales.csv')
    },
    {
      title: 'Calendar Events',
      description: 'Follow-up reminders as .ics for Google Calendar',
      icon: Calendar,
      color: 'from-amber-500 to-orange-600',
      action: () => handleDownload(api.exportCalendar(), 'leads_calendar.ics')
    },
    {
      title: 'Tasks Export',
      description: 'Lead follow-ups as TODO items for Google Tasks',
      icon: CheckSquare,
      color: 'from-cyan-500 to-blue-600',
      action: () => handleDownload(api.exportTasks(), 'leads_tasks.ics')
    }
  ];

  return (
    <div className="space-y-8 animate-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Download className="h-8 w-8 text-primary" />
          Export & Import
        </h1>
        <p className="text-muted-foreground mt-1">
          Export your data or import from CSV files
        </p>
      </div>

      {/* Export Section */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Export Data</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {exportOptions.map((option, index) => (
            <Card
              key={index}
              className="hover:shadow-lg transition-all cursor-pointer group"
              onClick={option.action}
            >
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${option.color} shadow-lg group-hover:scale-110 transition-transform`}>
                    <option.icon className="h-6 w-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold">{option.title}</h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {option.description}
                    </p>
                  </div>
                </div>
                <Button variant="outline" className="w-full mt-4 group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Import Section */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Import Data</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Upload className="h-5 w-5 text-primary" />
                Import Items from CSV
              </CardTitle>
              <CardDescription>
                Upload a CSV file to bulk import items into your inventory
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed rounded-lg p-8 text-center hover:border-primary transition-colors">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleImportCSV}
                  className="hidden"
                  id="csv-upload"
                  disabled={importing}
                />
                <label
                  htmlFor="csv-upload"
                  className="cursor-pointer"
                >
                  {importing ? (
                    <div className="flex flex-col items-center">
                      <RefreshCw className="h-12 w-12 text-primary animate-spin mb-4" />
                      <p className="font-medium">Importing...</p>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center">
                      <FileSpreadsheet className="h-12 w-12 text-muted-foreground mb-4" />
                      <p className="font-medium">Click to upload CSV</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        or drag and drop
                      </p>
                    </div>
                  )}
                </label>
              </div>

              <Button
                variant="outline"
                className="w-full"
                onClick={() => handleDownload(api.getTemplate(), 'items_template.csv')}
              >
                <FileText className="h-4 w-4 mr-2" />
                Download Template CSV
              </Button>

              {importResult && (
                <div className={`p-4 rounded-lg ${importResult.success ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'}`}>
                  {importResult.success ? (
                    <>
                      <p className="font-medium text-green-700 dark:text-green-400">
                        Import successful!
                      </p>
                      <p className="text-sm text-green-600 dark:text-green-500 mt-1">
                        Created {importResult.created} items
                      </p>
                    </>
                  ) : (
                    <>
                      <p className="font-medium text-red-700 dark:text-red-400">
                        Import failed
                      </p>
                      {importResult.errors?.length > 0 && (
                        <ul className="text-sm text-red-600 dark:text-red-500 mt-1">
                          {importResult.errors.map((err: string, i: number) => (
                            <li key={i}>{err}</li>
                          ))}
                        </ul>
                      )}
                    </>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Import Help */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">CSV Format Guide</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <p className="font-medium mb-2">Required Columns:</p>
                  <div className="flex flex-wrap gap-2">
                    <Badge>Name</Badge>
                  </div>
                </div>

                <div>
                  <p className="font-medium mb-2">Optional Columns:</p>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="outline">Description</Badge>
                    <Badge variant="outline">Category</Badge>
                    <Badge variant="outline">Condition</Badge>
                    <Badge variant="outline">Asking Price</Badge>
                    <Badge variant="outline">Min Price</Badge>
                    <Badge variant="outline">Cost Basis</Badge>
                    <Badge variant="outline">Status</Badge>
                    <Badge variant="outline">Platforms</Badge>
                    <Badge variant="outline">Notes</Badge>
                  </div>
                </div>

                <div className="bg-muted p-4 rounded-lg">
                  <p className="text-sm font-medium mb-2">Example Row:</p>
                  <code className="text-xs">
                    RTX 3080,NVIDIA Graphics Card,Graphics Card,good,500,450,700,draft,"reddit,ebay",Original box included
                  </code>
                </div>

                <div className="flex items-start gap-2 text-sm text-muted-foreground">
                  <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <p>
                    Platforms should be comma-separated (no spaces). Valid values: reddit, ebay, offerup, swappa, facebook
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Integration Info */}
      <Card className="bg-gradient-to-r from-primary/5 to-purple-500/5 border-primary/20">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-4">
            <div className="p-3 rounded-xl bg-primary/10">
              <Calendar className="h-8 w-8 text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold">Google Calendar & Tasks Integration</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Export your lead follow-ups as calendar events or tasks. Simply download the .ics file and import it into Google Calendar or any calendar app that supports iCalendar format.
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => handleDownload(api.exportCalendar(), 'leads_calendar.ics')}>
                <Calendar className="h-4 w-4 mr-2" />
                Calendar
              </Button>
              <Button variant="outline" onClick={() => handleDownload(api.exportTasks(), 'leads_tasks.ics')}>
                <CheckSquare className="h-4 w-4 mr-2" />
                Tasks
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
