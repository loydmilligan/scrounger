import React, { useState, useEffect } from 'react';
import {
  Settings,
  Key,
  Bot,
  Check,
  X,
  Plus,
  Star,
  Trash2,
  RefreshCw,
  ExternalLink,
  Search
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
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

interface AIModel {
  id: number;
  model_id: string;
  nickname: string;
  description?: string;
  model_type: string;
  cost_tier: string;
  context_length?: number;
  supports_streaming: boolean;
  supports_reasoning: boolean;
  is_favorite: boolean;
}

const MODEL_TYPES = [
  { value: 'general', label: 'General' },
  { value: 'coding', label: 'Coding' },
  { value: 'image', label: 'Image' },
  { value: 'reasoning', label: 'Reasoning' }
];

const COST_TIERS = [
  { value: '$', label: '$ - Cheap' },
  { value: '$$', label: '$$ - Mid-range' },
  { value: '$$$', label: '$$$ - Expensive' }
];

export default function SettingsPage() {
  const [settings, setSettings] = useState({ has_api_key: false, default_model: '' });
  const [apiKey, setApiKey] = useState('');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [saving, setSaving] = useState(false);

  const [models, setModels] = useState<AIModel[]>([]);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [modelDialogOpen, setModelDialogOpen] = useState(false);
  const [editingModel, setEditingModel] = useState<AIModel | null>(null);
  const [lookingUp, setLookingUp] = useState(false);

  const [modelForm, setModelForm] = useState({
    model_id: '',
    nickname: '',
    description: '',
    model_type: 'general',
    cost_tier: '$$',
    context_length: '',
    supports_streaming: true,
    supports_reasoning: false
  });

  useEffect(() => {
    fetchSettings();
    fetchModels();
  }, []);

  const fetchSettings = async () => {
    try {
      const data = await api.getAISettings();
      setSettings(data);
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    }
  };

  const fetchModels = async () => {
    setModelsLoading(true);
    try {
      const data = await api.getAIModels();
      setModels(data);
    } catch (error) {
      console.error('Failed to fetch models:', error);
    } finally {
      setModelsLoading(false);
    }
  };

  const handleSaveApiKey = async () => {
    if (!apiKey) return;
    setSaving(true);
    try {
      await api.updateAISettings({ openrouter_api_key: apiKey, default_model: settings.default_model });
      setApiKey('');
      fetchSettings();
      setTestResult({ success: true, message: 'API key saved successfully!' });
    } catch (error: any) {
      setTestResult({ success: false, message: error.message || 'Failed to save' });
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const result = await api.testAIConnection();
      setTestResult(result);
    } catch (error: any) {
      setTestResult({ success: false, message: error.message || 'Test failed' });
    } finally {
      setTesting(false);
    }
  };

  const handleLookupModel = async () => {
    if (!modelForm.model_id) return;
    setLookingUp(true);
    try {
      const data = await api.lookupModel(modelForm.model_id);
      setModelForm(prev => ({
        ...prev,
        nickname: data.nickname || prev.nickname,
        description: data.description || prev.description,
        cost_tier: data.cost_tier || prev.cost_tier,
        context_length: data.context_length?.toString() || prev.context_length,
        supports_streaming: data.supports_streaming ?? prev.supports_streaming,
        supports_reasoning: data.supports_reasoning ?? prev.supports_reasoning
      }));
    } catch (error: any) {
      alert(error.message || 'Model not found');
    } finally {
      setLookingUp(false);
    }
  };

  const handleSaveModel = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = {
        ...modelForm,
        context_length: modelForm.context_length ? parseInt(modelForm.context_length) : null
      };

      if (editingModel) {
        await api.updateAIModel(editingModel.id, data);
      } else {
        await api.createAIModel(data);
      }
      setModelDialogOpen(false);
      resetModelForm();
      fetchModels();
    } catch (error: any) {
      alert(error.message || 'Failed to save model');
    }
  };

  const handleDeleteModel = async (id: number) => {
    if (!confirm('Delete this model?')) return;
    try {
      await api.deleteAIModel(id);
      fetchModels();
    } catch (error) {
      console.error('Failed to delete model:', error);
    }
  };

  const handleToggleFavorite = async (id: number) => {
    try {
      await api.toggleFavorite(id);
      fetchModels();
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const handleSetDefaultModel = async (modelId: string) => {
    try {
      await api.updateAISettings({ default_model: modelId });
      fetchSettings();
    } catch (error) {
      console.error('Failed to set default model:', error);
    }
  };

  const resetModelForm = () => {
    setEditingModel(null);
    setModelForm({
      model_id: '',
      nickname: '',
      description: '',
      model_type: 'general',
      cost_tier: '$$',
      context_length: '',
      supports_streaming: true,
      supports_reasoning: false
    });
  };

  const openEditModel = (model: AIModel) => {
    setEditingModel(model);
    setModelForm({
      model_id: model.model_id,
      nickname: model.nickname,
      description: model.description || '',
      model_type: model.model_type,
      cost_tier: model.cost_tier,
      context_length: model.context_length?.toString() || '',
      supports_streaming: model.supports_streaming,
      supports_reasoning: model.supports_reasoning
    });
    setModelDialogOpen(true);
  };

  const getCostBadge = (tier: string) => {
    switch (tier) {
      case '$':
        return <Badge variant="success">{tier}</Badge>;
      case '$$':
        return <Badge variant="warning">{tier}</Badge>;
      case '$$$':
        return <Badge variant="destructive">{tier}</Badge>;
      default:
        return <Badge>{tier}</Badge>;
    }
  };

  return (
    <div className="space-y-8 animate-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <Settings className="h-8 w-8 text-primary" />
          Settings
        </h1>
        <p className="text-muted-foreground mt-1">
          Configure your OpenRouter API and AI models
        </p>
      </div>

      {/* API Key Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Key className="h-5 w-5 text-primary" />
            OpenRouter API Key
          </CardTitle>
          <CardDescription>
            Required for AI features like post generation, pricing help, and chat
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-2">
            <Badge variant={settings.has_api_key ? 'success' : 'secondary'}>
              {settings.has_api_key ? 'Configured' : 'Not configured'}
            </Badge>
            <a
              href="https://openrouter.ai/keys"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline flex items-center gap-1"
            >
              Get API key <ExternalLink className="h-3 w-3" />
            </a>
          </div>

          <div className="flex gap-2">
            <Input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-or-v1-..."
              className="flex-1"
            />
            <Button onClick={handleSaveApiKey} disabled={saving || !apiKey}>
              {saving ? <RefreshCw className="h-4 w-4 animate-spin" /> : 'Save'}
            </Button>
            <Button variant="outline" onClick={handleTestConnection} disabled={testing || !settings.has_api_key}>
              {testing ? <RefreshCw className="h-4 w-4 animate-spin" /> : 'Test'}
            </Button>
          </div>

          {testResult && (
            <div className={`flex items-center gap-2 text-sm ${testResult.success ? 'text-green-600' : 'text-red-600'}`}>
              {testResult.success ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}
              {testResult.message}
            </div>
          )}
        </CardContent>
      </Card>

      {/* AI Models Section */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              <Bot className="h-5 w-5 text-primary" />
              AI Models
            </CardTitle>
            <CardDescription>
              Manage your available AI models
            </CardDescription>
          </div>
          <Button onClick={() => { resetModelForm(); setModelDialogOpen(true); }}>
            <Plus className="h-4 w-4 mr-2" />
            Add Model
          </Button>
        </CardHeader>
        <CardContent>
          {modelsLoading ? (
            <div className="flex items-center justify-center h-32">
              <RefreshCw className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : models.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Bot className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p>No models configured</p>
              <Button
                variant="link"
                onClick={() => { resetModelForm(); setModelDialogOpen(true); }}
              >
                Add your first model
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {models.map((model) => (
                <div
                  key={model.id}
                  className={`flex items-center justify-between p-4 rounded-lg border ${
                    settings.default_model === model.model_id ? 'border-primary bg-primary/5' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleToggleFavorite(model.id)}
                      className={model.is_favorite ? 'text-amber-500' : 'text-muted-foreground'}
                    >
                      <Star className={`h-4 w-4 ${model.is_favorite ? 'fill-current' : ''}`} />
                    </Button>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{model.nickname}</span>
                        {getCostBadge(model.cost_tier)}
                        {settings.default_model === model.model_id && (
                          <Badge variant="default">Default</Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{model.model_id}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {settings.default_model !== model.model_id && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleSetDefaultModel(model.model_id)}
                      >
                        Set Default
                      </Button>
                    )}
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => openEditModel(model)}
                    >
                      <Settings className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => handleDeleteModel(model.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add/Edit Model Dialog */}
      <Dialog open={modelDialogOpen} onOpenChange={setModelDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>
              {editingModel ? 'Edit Model' : 'Add New Model'}
            </DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSaveModel} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Model ID *</label>
              <div className="flex gap-2">
                <Input
                  value={modelForm.model_id}
                  onChange={(e) => setModelForm({ ...modelForm, model_id: e.target.value })}
                  placeholder="anthropic/claude-3.5-sonnet"
                  disabled={!!editingModel}
                  required
                />
                {!editingModel && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleLookupModel}
                    disabled={lookingUp || !modelForm.model_id}
                  >
                    {lookingUp ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                  </Button>
                )}
              </div>
            </div>

            <div>
              <label className="text-sm font-medium">Nickname *</label>
              <Input
                value={modelForm.nickname}
                onChange={(e) => setModelForm({ ...modelForm, nickname: e.target.value })}
                placeholder="Claude 3.5 Sonnet"
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium">Description</label>
              <textarea
                value={modelForm.description}
                onChange={(e) => setModelForm({ ...modelForm, description: e.target.value })}
                placeholder="A great all-around model..."
                className="w-full min-h-[60px] px-3 py-2 rounded-md border bg-background text-sm"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Model Type</label>
                <Select
                  value={modelForm.model_type}
                  onValueChange={(value) => setModelForm({ ...modelForm, model_type: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {MODEL_TYPES.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium">Cost Tier</label>
                <Select
                  value={modelForm.cost_tier}
                  onValueChange={(value) => setModelForm({ ...modelForm, cost_tier: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {COST_TIERS.map(tier => (
                      <SelectItem key={tier.value} value={tier.value}>
                        {tier.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium">Context Length</label>
              <Input
                type="number"
                value={modelForm.context_length}
                onChange={(e) => setModelForm({ ...modelForm, context_length: e.target.value })}
                placeholder="128000"
              />
            </div>

            <div className="flex gap-4">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={modelForm.supports_streaming}
                  onChange={(e) => setModelForm({ ...modelForm, supports_streaming: e.target.checked })}
                  className="rounded"
                />
                Supports Streaming
              </label>

              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={modelForm.supports_reasoning}
                  onChange={(e) => setModelForm({ ...modelForm, supports_reasoning: e.target.checked })}
                  className="rounded"
                />
                Deep Reasoning
              </label>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setModelDialogOpen(false)}>
                Cancel
              </Button>
              <Button type="submit">
                {editingModel ? 'Save Changes' : 'Add Model'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
