import React, { useState, useEffect } from 'react';
import {
  Bot,
  Send,
  FileText,
  DollarSign,
  Package as PackageIcon,
  Truck,
  RefreshCw,
  Copy,
  Check,
  Link,
  Layers
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { api } from '@/utils/api';

export default function AIAssistant() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');
  const [copied, setCopied] = useState(false);

  // Post Generator
  const [selectedItemId, setSelectedItemId] = useState('');
  const [platform, setPlatform] = useState('reddit');
  const [subreddit, setSubreddit] = useState('hardwareswap');

  // Price Check
  const [itemName, setItemName] = useState('');
  const [condition, setCondition] = useState('good');
  const [description, setDescription] = useState('');

  // Shipping
  const [weight, setWeight] = useState('');
  const [length, setLength] = useState('');
  const [width, setWidth] = useState('');
  const [height, setHeight] = useState('');
  const [fromZip, setFromZip] = useState('');
  const [toZip, setToZip] = useState('');

  // Chat
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<Array<{ role: string; content: string }>>([]);

  // Bundle Parser
  const [bundleUrl, setBundleUrl] = useState('');
  const [createItems, setCreateItems] = useState(false);
  const [parsedItems, setParsedItems] = useState<any[]>([]);

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const data = await api.getItems({});
      setItems(data.items || []);
    } catch (error) {
      console.error('Failed to fetch items:', error);
    }
  };

  const handleGeneratePost = async () => {
    if (!selectedItemId) return;
    setLoading(true);
    setResult('');
    try {
      const response = await api.generatePost({
        item_id: parseInt(selectedItemId),
        platform,
        subreddit: platform === 'reddit' ? subreddit : undefined
      });
      setResult(response.post);
    } catch (error: any) {
      setResult('Error: ' + (error.message || 'Failed to generate post'));
    } finally {
      setLoading(false);
    }
  };

  const handlePriceCheck = async () => {
    if (!itemName) return;
    setLoading(true);
    setResult('');
    try {
      const response = await api.priceCheck({
        item_name: itemName,
        condition,
        description: description || undefined
      });
      setResult(response.suggestions);
    } catch (error: any) {
      setResult('Error: ' + (error.message || 'Failed to get price suggestions'));
    } finally {
      setLoading(false);
    }
  };

  const handleShippingHelp = async () => {
    if (!weight || !length || !width || !height || !fromZip || !toZip) return;
    setLoading(true);
    setResult('');
    try {
      const response = await api.shippingHelp({
        weight_lbs: parseFloat(weight),
        length_in: parseFloat(length),
        width_in: parseFloat(width),
        height_in: parseFloat(height),
        from_zip: fromZip,
        to_zip: toZip
      });
      setResult(response.shipping_info);
    } catch (error: any) {
      setResult('Error: ' + (error.message || 'Failed to get shipping info'));
    } finally {
      setLoading(false);
    }
  };

  const handleChat = async () => {
    if (!chatMessage.trim()) return;

    const newMessage = { role: 'user', content: chatMessage };
    const updatedHistory = [...chatHistory, newMessage];
    setChatHistory(updatedHistory);
    setChatMessage('');
    setLoading(true);

    try {
      const response = await api.chat({
        messages: updatedHistory,
        system_prompt: 'You are a helpful assistant for selling items online. Help with pricing, listings, shipping, and sales strategies for platforms like Reddit (r/hardwareswap, r/homelabsales), eBay, Swappa, and OfferUp.'
      });

      setChatHistory([...updatedHistory, { role: 'assistant', content: response.content }]);
    } catch (error: any) {
      setChatHistory([...updatedHistory, { role: 'assistant', content: 'Error: ' + (error.message || 'Failed to get response') }]);
    } finally {
      setLoading(false);
    }
  };

  const handleParseBundle = async () => {
    if (!bundleUrl) return;
    setLoading(true);
    setParsedItems([]);
    setResult('');
    try {
      const response = await api.parseBundle({
        url: bundleUrl,
        create_items: createItems
      });
      setParsedItems(response.items || []);
      if (response.created_items?.length > 0) {
        setResult(`Created ${response.created_items.length} items in inventory`);
        fetchItems(); // Refresh items list
      }
    } catch (error: any) {
      setResult('Error: ' + (error.message || 'Failed to parse bundle'));
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(result);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6 animate-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Bot className="h-8 w-8 text-primary" />
            AI Assistant
          </h1>
          <p className="text-muted-foreground mt-1">
            Get help with listings, pricing, and shipping
          </p>
        </div>
      </div>

      <Tabs defaultValue="post" className="space-y-6">
        <TabsList className="grid grid-cols-5 w-full max-w-2xl">
          <TabsTrigger value="post" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            <span className="hidden sm:inline">Post</span>
          </TabsTrigger>
          <TabsTrigger value="bundle" className="flex items-center gap-2">
            <Layers className="h-4 w-4" />
            <span className="hidden sm:inline">Bundle</span>
          </TabsTrigger>
          <TabsTrigger value="price" className="flex items-center gap-2">
            <DollarSign className="h-4 w-4" />
            <span className="hidden sm:inline">Price</span>
          </TabsTrigger>
          <TabsTrigger value="shipping" className="flex items-center gap-2">
            <Truck className="h-4 w-4" />
            <span className="hidden sm:inline">Ship</span>
          </TabsTrigger>
          <TabsTrigger value="chat" className="flex items-center gap-2">
            <Bot className="h-4 w-4" />
            <span className="hidden sm:inline">Chat</span>
          </TabsTrigger>
        </TabsList>

        {/* Generate Post Tab */}
        <TabsContent value="post">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <FileText className="h-5 w-5 text-primary" />
                  Generate Sales Post
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Select Item</label>
                  <Select value={selectedItemId} onValueChange={setSelectedItemId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choose an item" />
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
                  <label className="text-sm font-medium">Platform</label>
                  <Select value={platform} onValueChange={setPlatform}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="reddit">Reddit</SelectItem>
                      <SelectItem value="ebay">eBay</SelectItem>
                      <SelectItem value="offerup">OfferUp</SelectItem>
                      <SelectItem value="swappa">Swappa</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {platform === 'reddit' && (
                  <div>
                    <label className="text-sm font-medium">Subreddit</label>
                    <Select value={subreddit} onValueChange={setSubreddit}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="hardwareswap">r/hardwareswap</SelectItem>
                        <SelectItem value="homelabsales">r/homelabsales</SelectItem>
                        <SelectItem value="appleswap">r/appleswap</SelectItem>
                        <SelectItem value="AVexchange">r/AVexchange</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                )}

                <Button
                  onClick={handleGeneratePost}
                  disabled={loading || !selectedItemId}
                  className="w-full"
                >
                  {loading ? (
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <FileText className="h-4 w-4 mr-2" />
                  )}
                  Generate Post
                </Button>
              </CardContent>
            </Card>

            {/* Result Card */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-lg">Generated Post</CardTitle>
                {result && (
                  <Button variant="outline" size="sm" onClick={copyToClipboard}>
                    {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  </Button>
                )}
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex items-center justify-center h-48">
                    <RefreshCw className="h-8 w-8 animate-spin text-primary" />
                  </div>
                ) : result ? (
                  <pre className="whitespace-pre-wrap text-sm bg-muted p-4 rounded-lg overflow-auto max-h-96">
                    {result}
                  </pre>
                ) : (
                  <div className="flex items-center justify-center h-48 text-muted-foreground">
                    Select an item and generate a post
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Bundle Parser Tab */}
        <TabsContent value="bundle">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Layers className="h-5 w-5 text-primary" />
                  Parse Reddit Bundle
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Reddit Post URL *</label>
                  <Input
                    value={bundleUrl}
                    onChange={(e) => setBundleUrl(e.target.value)}
                    placeholder="https://www.reddit.com/r/hardwareswap/comments/..."
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Paste a Reddit sales post URL to extract individual items
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="createItems"
                    checked={createItems}
                    onChange={(e) => setCreateItems(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <label htmlFor="createItems" className="text-sm">
                    Auto-create items in inventory
                  </label>
                </div>

                <Button
                  onClick={handleParseBundle}
                  disabled={loading || !bundleUrl}
                  className="w-full"
                >
                  {loading ? (
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Layers className="h-4 w-4 mr-2" />
                  )}
                  Parse Bundle
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">
                  Extracted Items {parsedItems.length > 0 && `(${parsedItems.length})`}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex items-center justify-center h-48">
                    <RefreshCw className="h-8 w-8 animate-spin text-primary" />
                  </div>
                ) : parsedItems.length > 0 ? (
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {parsedItems.map((item: any, index: number) => (
                      <div
                        key={index}
                        className="p-3 rounded-lg border bg-card hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-medium">{item.name}</h4>
                            <p className="text-sm text-muted-foreground">
                              {item.description}
                            </p>
                          </div>
                          {item.asking_price && (
                            <Badge variant="success" className="ml-2">
                              ${item.asking_price}
                            </Badge>
                          )}
                        </div>
                        <div className="flex gap-2 mt-2">
                          <Badge variant="outline" className="text-xs">
                            {item.category || 'Uncategorized'}
                          </Badge>
                          <Badge variant="secondary" className="text-xs capitalize">
                            {item.condition?.replace('_', ' ') || 'Unknown'}
                          </Badge>
                        </div>
                      </div>
                    ))}
                    {result && (
                      <p className="text-sm text-green-600 mt-2">{result}</p>
                    )}
                  </div>
                ) : result ? (
                  <div className="text-red-500 text-sm">{result}</div>
                ) : (
                  <div className="flex items-center justify-center h-48 text-muted-foreground">
                    <div className="text-center">
                      <Link className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>Paste a Reddit URL to extract items</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Price Check Tab */}
        <TabsContent value="price">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <DollarSign className="h-5 w-5 text-primary" />
                  Price Research
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Item Name *</label>
                  <Input
                    value={itemName}
                    onChange={(e) => setItemName(e.target.value)}
                    placeholder="e.g., NVIDIA RTX 3080 FE"
                  />
                </div>

                <div>
                  <label className="text-sm font-medium">Condition</label>
                  <Select value={condition} onValueChange={setCondition}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="new">New / Sealed</SelectItem>
                      <SelectItem value="like_new">Like New</SelectItem>
                      <SelectItem value="good">Good</SelectItem>
                      <SelectItem value="fair">Fair</SelectItem>
                      <SelectItem value="poor">Poor</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium">Additional Details</label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Any relevant details..."
                    className="w-full min-h-[80px] px-3 py-2 rounded-md border bg-background text-sm"
                  />
                </div>

                <Button
                  onClick={handlePriceCheck}
                  disabled={loading || !itemName}
                  className="w-full"
                >
                  {loading ? (
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <DollarSign className="h-4 w-4 mr-2" />
                  )}
                  Get Price Suggestions
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Price Suggestions</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex items-center justify-center h-48">
                    <RefreshCw className="h-8 w-8 animate-spin text-primary" />
                  </div>
                ) : result ? (
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap text-sm bg-muted p-4 rounded-lg overflow-auto max-h-96">
                      {result}
                    </pre>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-48 text-muted-foreground">
                    Enter item details to get pricing suggestions
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Shipping Tab */}
        <TabsContent value="shipping">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Truck className="h-5 w-5 text-primary" />
                  Shipping Calculator
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Weight (lbs) *</label>
                    <Input
                      type="number"
                      step="0.1"
                      value={weight}
                      onChange={(e) => setWeight(e.target.value)}
                      placeholder="0.0"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Length (in) *</label>
                    <Input
                      type="number"
                      step="0.1"
                      value={length}
                      onChange={(e) => setLength(e.target.value)}
                      placeholder="0.0"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Width (in) *</label>
                    <Input
                      type="number"
                      step="0.1"
                      value={width}
                      onChange={(e) => setWidth(e.target.value)}
                      placeholder="0.0"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Height (in) *</label>
                    <Input
                      type="number"
                      step="0.1"
                      value={height}
                      onChange={(e) => setHeight(e.target.value)}
                      placeholder="0.0"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">From ZIP *</label>
                    <Input
                      value={fromZip}
                      onChange={(e) => setFromZip(e.target.value)}
                      placeholder="12345"
                      maxLength={5}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">To ZIP *</label>
                    <Input
                      value={toZip}
                      onChange={(e) => setToZip(e.target.value)}
                      placeholder="67890"
                      maxLength={5}
                    />
                  </div>
                </div>

                <Button
                  onClick={handleShippingHelp}
                  disabled={loading || !weight || !length || !width || !height || !fromZip || !toZip}
                  className="w-full"
                >
                  {loading ? (
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Truck className="h-4 w-4 mr-2" />
                  )}
                  Calculate Shipping
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Shipping Options</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex items-center justify-center h-48">
                    <RefreshCw className="h-8 w-8 animate-spin text-primary" />
                  </div>
                ) : result ? (
                  <pre className="whitespace-pre-wrap text-sm bg-muted p-4 rounded-lg overflow-auto max-h-96">
                    {result}
                  </pre>
                ) : (
                  <div className="flex items-center justify-center h-48 text-muted-foreground">
                    Enter package details to get shipping estimates
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Chat Tab */}
        <TabsContent value="chat">
          <Card className="h-[600px] flex flex-col">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Bot className="h-5 w-5 text-primary" />
                AI Chat
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col overflow-hidden">
              <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                {chatHistory.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
                    <Bot className="h-16 w-16 mb-4 opacity-50" />
                    <p>Ask me anything about selling items online!</p>
                    <p className="text-sm mt-2">
                      Tips for r/hardwareswap, pricing help, shipping advice, and more.
                    </p>
                  </div>
                ) : (
                  chatHistory.map((msg, i) => (
                    <div
                      key={i}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] p-3 rounded-lg ${
                          msg.role === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted'
                        }`}
                      >
                        <pre className="whitespace-pre-wrap text-sm font-sans">
                          {msg.content}
                        </pre>
                      </div>
                    </div>
                  ))
                )}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-muted p-3 rounded-lg">
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    </div>
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                <Input
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  placeholder="Ask about pricing, shipping, listings..."
                  onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleChat()}
                  disabled={loading}
                />
                <Button onClick={handleChat} disabled={loading || !chatMessage.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
