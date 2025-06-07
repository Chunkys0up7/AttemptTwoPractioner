import React, { useState, FormEvent, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '@components/common/Button';
import Card from '@components/common/Card';
import { FormRow } from '@components/common/FormRow';
import { Input } from '@components/common/Input';
import { Select } from '@components/common/Select';
import { TextArea } from '@components/common/TextArea';
import { UploadIcon, CheckCircleIcon, XCircleIcon, PlusCircleIcon, TrashIcon } from '@components/icons';
import ChatAssistant from '@components/submit_component/ChatAssistant';
import CodeEditor from '@components/workflow/CodeEditor';
import { useComponents } from '@context/ComponentContext';
import { AIComponent, SpecificComponentType, NotebookCell, AIComponentCostTier } from '../types';
import { SUBMITTABLE_COMPONENT_TYPES, COMPONENT_COMPLIANCE_OPTIONS, COMPONENT_COST_TIERS, COMPONENT_VISIBILITY_OPTIONS, LLM_MODELS, getIconForComponentType } from '../constants';

interface TypeSpecificData {
  codeContent?: string;
  notebookCells?: NotebookCell[];
  mcpConfiguration?: string;
  streamlitAppData?: {
    gitRepoUrl?: string;
    mainScriptPath?: string;
    requirements?: string;
  };
  llmAgentData?: {
    model?: string;
    systemPrompt?: string;
    userPromptTemplate?: string;
    temperature?: number;
    maxTokens?: number;
  };
}

interface TypeSpecificFormProps {
  data: TypeSpecificData;
  onChange: (key: keyof TypeSpecificData, value: any) => void;
  errors: Partial<Record<keyof TypeSpecificData, string>>;
}

// --- Sub-Form Components ---

const CodeEditorForm: React.FC<TypeSpecificFormProps & { language: string }> = ({ data, onChange, errors, language }) => (
  <div>
    <label htmlFor="codeContent" className="block text-sm font-medium text-neutral-700 mb-1">
      {language} Code <span className="text-red-500">*</span>
    </label>
    <CodeEditor
      value={data?.codeContent || ''}
      language={language.toLowerCase()}
      onChange={(value: string | undefined) => onChange('codeContent', value || '')}
      height="300px"
    />
    {errors?.codeContent && <p className="mt-1 text-xs text-red-500">{errors.codeContent}</p>}
  </div>
);

const NotebookEditorForm: React.FC<TypeSpecificFormProps> = ({ data, onChange, errors }) => {
  const cells = data?.notebookCells || [];

  const addCell = (type: 'code' | 'markdown') => {
    const newCell: NotebookCell = { id: `cell-${Date.now()}`, type, content: '' };
    onChange('notebookCells', [...cells, newCell]);
  };

  const updateCellContent = (id: string, content: string) => {
    onChange('notebookCells', cells.map(cell => cell.id === id ? { ...cell, content } : cell));
  };

  const removeCell = (id: string) => {
    onChange('notebookCells', cells.filter(cell => cell.id !== id));
  };
  
  const changeCellType = (id: string, type: 'code' | 'markdown') => {
    onChange('notebookCells', cells.map(cell => cell.id === id ? { ...cell, type } : cell));
  };

  return (
    <div>
      <label className="block text-sm font-medium text-neutral-700 mb-2">Notebook Cells</label>
      {cells.map((cell, index) => (
        <Card key={cell.id} className="mb-3 bg-neutral-50" noPadding>
          <div className="p-3 border-b border-neutral-200">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-semibold text-neutral-600">Cell {index + 1} ({cell.type})</span>
              <div>
                <select 
                  value={cell.type} 
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) => changeCellType(cell.id, e.target.value as 'code' | 'markdown')}
                  className="text-xs p-1 border border-neutral-300 rounded-md mr-2 bg-white text-neutral-900 placeholder-neutral-500"
                >
                  <option value="code">Code</option>
                  <option value="markdown">Markdown</option>
                </select>
                <Button variant="danger" size="sm" onClick={() => removeCell(cell.id)} className="!p-1">
                  <TrashIcon className="w-3.5 h-3.5" />
                </Button>
              </div>
            </div>
            {cell.type === 'code' ? (
              <CodeEditor
                value={cell.content}
                language="python"
                onChange={(value: string | undefined) => updateCellContent(cell.id, value || '')}
                height="150px"
              />
            ) : (
              <TextArea
                value={cell.content}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => updateCellContent(cell.id, e.target.value)}
                rows={3}
                placeholder="Enter markdown content..."
              />
            )}
          </div>
        </Card>
      ))}
      <div className="flex gap-2 mt-2">
        <Button variant="secondary" size="sm" onClick={() => addCell('code')}>
          <PlusCircleIcon className="w-4 h-4 mr-1" />
          Add Code Cell
        </Button>
        <Button variant="secondary" size="sm" onClick={() => addCell('markdown')}>
          <PlusCircleIcon className="w-4 h-4 mr-1" />
          Add Markdown Cell
        </Button>
      </div>
    </div>
  );
};

const LLMAgentEditorForm: React.FC<TypeSpecificFormProps> = ({ data, onChange, errors }) => {
  const llmData = data?.llmPrompt || {};
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const val = type === 'number' ? parseFloat(value) : value;
    onChange('llmPrompt', { ...llmData, [name]: val });
  };

  return (
    <div className="space-y-4">
      <FormRow label="LLM Model" htmlFor="model">
        <select name="model" id="model" value={llmData.model || ''} onChange={handleChange}
                className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm bg-white text-neutral-900 placeholder-neutral-500">
          <option value="">Select Model</option>
          {LLM_MODELS.map(m => <option key={m} value={m}>{m}</option>)}
        </select>
      </FormRow>
      <FormRow label="System Prompt" htmlFor="systemPrompt">
        <textarea name="systemPrompt" id="systemPrompt" value={llmData.systemPrompt || ''} onChange={handleChange} rows={3}
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm bg-white text-neutral-900 placeholder-neutral-500" />
      </FormRow>
      <FormRow label="User Prompt Template" htmlFor="userPromptTemplate">
        <textarea name="userPromptTemplate" id="userPromptTemplate" value={llmData.userPromptTemplate || ''} onChange={handleChange} rows={3}
                  className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm bg-white text-neutral-900 placeholder-neutral-500" placeholder="e.g., Summarize this: {{inputText}}" />
      </FormRow>
      <div className="grid grid-cols-2 gap-4">
        <FormRow label="Temperature" htmlFor="temperature">
          <input type="number" name="temperature" id="temperature" value={llmData.temperature || ''} onChange={handleChange} step="0.1" min="0" max="2"
                 className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm bg-white text-neutral-900 placeholder-neutral-500" />
        </FormRow>
        <FormRow label="Max Tokens" htmlFor="maxTokens">
          <input type="number" name="maxTokens" id="maxTokens" value={llmData.maxTokens || ''} onChange={handleChange} step="1" min="1"
                 className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm bg-white text-neutral-900 placeholder-neutral-500" />
        </FormRow>
      </div>
       {errors?.llmPrompt && <p className="mt-1 text-xs text-red-500">{errors.llmPrompt as string}</p>}
    </div>
  );
};

const StreamlitAppEditorForm: React.FC<TypeSpecificFormProps> = ({ data, onChange, errors }) => {
  const streamlitData = data?.streamlitAppData || {};
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    onChange('streamlitAppData', { ...streamlitData, [name]: value });
  };
  return (
    <div className="space-y-4">
      <FormRow label="Git Repository URL" htmlFor="gitRepoUrl">
        <Input
          type="url"
          name="gitRepoUrl"
          id="gitRepoUrl"
          value={streamlitData.gitRepoUrl || ''}
          onChange={handleChange}
          placeholder="https://github.com/user/repo.git"
        />
      </FormRow>
      <FormRow label="Main Script Path (e.g., app.py)" htmlFor="mainScriptPath">
        <Input
          type="text"
          name="mainScriptPath"
          id="mainScriptPath"
          value={streamlitData.mainScriptPath || ''}
          onChange={handleChange}
          placeholder="app.py"
        />
      </FormRow>
      <FormRow label="Requirements (content of requirements.txt)" htmlFor="requirements">
        <TextArea
          name="requirements"
          id="requirements"
          value={streamlitData.requirements || ''}
          onChange={handleChange}
          rows={5}
          placeholder="streamlit\npandas\n..."
        />
      </FormRow>
      {errors?.streamlitAppData && <p className="mt-1 text-xs text-red-500">{errors.streamlitAppData as string}</p>}
    </div>
  );
};

const MCPEditorForm: React.FC<TypeSpecificFormProps> = ({ data, onChange, errors }) => (
  <div>
    <label htmlFor="mcpConfiguration" className="block text-sm font-medium text-neutral-700 mb-1">
      MCP Configuration (JSON/YAML) <span className="text-red-500">*</span>
    </label>
    <CodeEditor
      value={data?.mcpConfiguration || ''}
      language="yaml"
      onChange={(value: string | undefined) => onChange('mcpConfiguration', value || '')}
      height="300px"
    />
    {errors?.mcpConfiguration && <p className="mt-1 text-xs text-red-500">{errors.mcpConfiguration}</p>}
  </div>
);

// --- Main Submit Component Page ---

interface CommonFormData {
  name: string;
  description: string;
  version: string;
  tags: string; 
  inputSchema: string;
  outputSchema: string;
  compliance: string[];
  costTier: AIComponentCostTier;
  visibility: AIComponent['visibility'];
}

/**
 * Page for users to submit new AI components.
 * Features dynamic forms based on component type and an AI chat assistant.
 * @returns {JSX.Element} The SubmitComponentPage component.
 */
const SubmitComponentPage: React.FC = () => {
  const navigate = useNavigate();
  const { addCustomComponent } = useComponents();
  
  const [selectedType, setSelectedType] = useState<SpecificComponentType | ''>('');
  
  const [commonFormData, setCommonFormData] = useState<CommonFormData>({
    name: '', description: '', version: '1.0.0', tags: '',
    inputSchema: '', outputSchema: '', compliance: [], costTier: 'Free', visibility: 'Private',
  });
  const [typeSpecificData, setTypeSpecificData] = useState<TypeSpecificData>({
    llmPrompt: '',
    codeContent: '',
  });
  
  const [errors, setErrors] = useState<Partial<Record<keyof CommonFormData | keyof TypeSpecificData, string>>>({});
  const [submissionStatus, setSubmissionStatus] = useState<'idle' | 'success' | 'error'>('idle');

  /** Handles changes for common form fields. */
  const handleCommonChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setCommonFormData(prev => ({ ...prev, [name]: value }));
    setErrors(prev => ({ ...prev, [name as keyof CommonFormData]: undefined }));
  };

  /** Handles changes for checkbox groups (compliance). */
  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, checked } = e.target;
    setCommonFormData(prev => {
      const currentValues = prev[name as 'compliance'] as string[];
      if (checked) {
        return { ...prev, [name]: [...currentValues, value] };
      } else {
        return { ...prev, [name]: currentValues.filter(item => item !== value) };
      }
    });
  };
  
  /** Handles changes for type-specific form fields. */
  const handleTypeSpecificChange = (key: keyof TypeSpecificData, value: string) => {
    setTypeSpecificData((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const setTypeSpecificError = (field: keyof TypeSpecificData, error: string | undefined) => {
    setErrors(prev => ({ ...prev, [field]: error }));
  };

  useEffect(() => {
    // Reset typeSpecificData and related errors when type changes
    setTypeSpecificData({
      llmPrompt: '',
      codeContent: '',
    });
    setErrors(prev => {
        const commonErrors: Partial<Record<keyof CommonFormData, string>> = {};
        (Object.keys(prev) as Array<keyof typeof prev>).forEach(key => {
            if (key in commonFormData) {
                commonErrors[key as keyof CommonFormData] = prev[key];
            }
        });
        return commonErrors;
    });
  }, [selectedType]);


  /** Validates the form data. */
  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof CommonFormData | keyof TypeSpecificData, string>> = {};
    if (!selectedType) newErrors.name = 'Please select a component type.'; // Using 'name' field for general type error
    if (!commonFormData.name.trim()) newErrors.name = 'Component name is required.';
    if (!commonFormData.description.trim()) newErrors.description = 'Description is required.';
    if (!commonFormData.version.trim()) newErrors.version = 'Version is required.';
    else if (!/^\d+\.\d+\.\d+([-.].+)?$/.test(commonFormData.version)) newErrors.version = 'Version must be in semver format (e.g., 1.0.0 or 1.0.0-alpha.1).';

    if (commonFormData.inputSchema.trim()) {
      try { JSON.parse(commonFormData.inputSchema); } 
      catch (e) { newErrors.inputSchema = 'Input Schema must be valid JSON.'; }
    }
    if (commonFormData.outputSchema.trim()) {
      try { JSON.parse(commonFormData.outputSchema); } 
      catch (e) { newErrors.outputSchema = 'Output Schema must be valid JSON.'; }
    }

    // Type-specific validations
    if (selectedType === 'Python Script' || selectedType === 'TypeScript Script') {
        if (!typeSpecificData?.codeContent?.trim()) newErrors.codeContent = 'Code content is required.';
    } else if (selectedType === 'Jupyter Notebook') {
        if (!typeSpecificData?.notebookCells || typeSpecificData.notebookCells.length === 0) {
            newErrors.notebookCells = 'At least one notebook cell is required.';
        } else if (typeSpecificData.notebookCells.some(cell => !cell.content.trim())) {
            newErrors.notebookCells = 'All notebook cells must have content.';
        }
    } else if (selectedType === 'MCP') {
        if (!typeSpecificData?.mcpConfiguration?.trim()) newErrors.mcpConfiguration = 'MCP Configuration is required.';
        // Could add JSON/YAML validation here
    } // Add more for LLM Agent, Streamlit as needed

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /** Handles form submission. */
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSubmissionStatus('idle');
    if (!validateForm()) {
      setSubmissionStatus('error');
      return;
    }

    try {
      const componentToAdd: Omit<AIComponent, 'id' | 'icon' | 'isCustom'> = {
        name: commonFormData.name,
        description: commonFormData.description,
        version: commonFormData.version,
        type: selectedType as SpecificComponentType, // Cast as it's validated
        tags: commonFormData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        inputSchema: commonFormData.inputSchema ? JSON.parse(commonFormData.inputSchema) : undefined,
        outputSchema: commonFormData.outputSchema ? JSON.parse(commonFormData.outputSchema) : undefined,
        compliance: commonFormData.compliance,
        costTier: commonFormData.costTier,
        visibility: commonFormData.visibility,
        typeSpecificData: typeSpecificData,
      };
      addCustomComponent(componentToAdd);
      setSubmissionStatus('success');
      setTimeout(() => {
        navigate('/marketplace');
      }, 1500);
    } catch (error) {
      console.error("Error submitting component:", error);
      setSubmissionStatus('error');
      setErrors(prev => ({ ...prev, name: "Submission failed. Check console for details."}));
    }
  };
  
  const renderTypeSpecificForm = () => {
    if (!selectedType) return null;
    const props = { data: typeSpecificData, onChange: handleTypeSpecificChange, setFormError: setTypeSpecificError, errors: errors as any };
    switch (selectedType) {
      case 'Python Script': return <CodeEditorForm {...props} language="Python" />;
      case 'TypeScript Script': return <CodeEditorForm {...props} language="TypeScript" />;
      case 'Jupyter Notebook': return <NotebookEditorForm {...props} />;
      case 'LLM Prompt Agent': return <LLMAgentEditorForm {...props} />;
      case 'Streamlit App': return <StreamlitAppEditorForm {...props} />;
      case 'MCP': return <MCPEditorForm {...props} />;
      // For 'Data', 'Utility', 'Output', no specific fields are defined yet, could add simple text field if needed
      case 'Data':
      case 'Utility':
      case 'Output':
        return <p className="text-sm text-neutral-500 p-3 bg-neutral-50 rounded-md">No additional configuration needed for '{selectedType}' type beyond common details. You can specify behavior via Input/Output schemas.</p>;
      default: return null;
    }
  };

  let currentFullComponentDataInputSchema: Record<string, any> | undefined;
  try {
    currentFullComponentDataInputSchema = commonFormData.inputSchema ? JSON.parse(commonFormData.inputSchema) : undefined;
  } catch {
    currentFullComponentDataInputSchema = { error: "Invalid JSON in input schema" };
  }

  let currentFullComponentDataOutputSchema: Record<string, any> | undefined;
  try {
    currentFullComponentDataOutputSchema = commonFormData.outputSchema ? JSON.parse(commonFormData.outputSchema) : undefined;
  } catch {
    currentFullComponentDataOutputSchema = { error: "Invalid JSON in output schema" };
  }
  
  const currentFullComponentData: Partial<AIComponent> = {
    name: commonFormData.name,
    description: commonFormData.description,
    version: commonFormData.version,
    tags: commonFormData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
    inputSchema: currentFullComponentDataInputSchema,
    outputSchema: currentFullComponentDataOutputSchema,
    compliance: commonFormData.compliance,
    costTier: commonFormData.costTier,
    visibility: commonFormData.visibility,
    type: selectedType || undefined,
    typeSpecificData,
  };


  return (
    <div className="pb-16"> {/* Add padding to bottom to avoid overlap with fixed chat */}
      <header className="mb-6">
        <h1 className="text-3xl font-bold text-neutral-800">Submit New Component</h1>
        <p className="text-neutral-600 mt-1">Contribute a new AI component to the ecosystem. Use the AI Assistant for help!</p>
      </header>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-6">
          <FormRow label="Component Type" htmlFor="componentType" error={errors.name && selectedType === '' ? errors.name : undefined} required>
            <select name="componentType" id="componentType" value={selectedType} 
                    onChange={(e) => setSelectedType(e.target.value as SpecificComponentType | '')}
                    className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm bg-white text-neutral-900 placeholder-neutral-500">
              <option value="">-- Select Component Type --</option>
              {SUBMITTABLE_COMPONENT_TYPES.map(type => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </FormRow>

          {selectedType && (
            <>
              <div className="flex items-center space-x-2 text-lg font-medium text-primary mt-4 mb-2 pt-4 border-t border-neutral-200">
                {getIconForComponentType(selectedType, {className: "w-6 h-6"})}
                <span>Configuring: {selectedType}</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormRow label="Component Name" htmlFor="name" error={errors.name} required>
                  <input type="text" name="name" id="name" value={commonFormData.name} onChange={handleCommonChange}
                        className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm bg-white text-neutral-900 placeholder-neutral-500" />
                </FormRow>
                <FormRow label="Version" htmlFor="version" error={errors.version} required>
                  <input type="text" name="version" id="version" value={commonFormData.version} onChange={handleCommonChange}
                        className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm bg-white text-neutral-900 placeholder-neutral-500" placeholder="e.g., 1.0.0" />
                </FormRow>
              </div>

              <FormRow label="Description" htmlFor="description" error={errors.description} required>
                <textarea name="description" id="description" value={commonFormData.description} onChange={handleCommonChange} rows={3}
                          className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm bg-white text-neutral-900 placeholder-neutral-500" />
              </FormRow>
              
              {/* Type Specific Form Area */}
              <div className="p-4 border border-neutral-200 rounded-lg bg-neutral-50/50 my-4">
                <h3 className="text-md font-semibold text-neutral-700 mb-3 border-b pb-2 border-neutral-200">Type-Specific Configuration</h3>
                {renderTypeSpecificForm()}
              </div>


              <FormRow label="Tags (comma-separated)" htmlFor="tags" error={errors.tags}>
                <input type="text" name="tags" id="tags" value={commonFormData.tags} onChange={handleCommonChange}
                      className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm bg-white text-neutral-900 placeholder-neutral-500" />
              </FormRow>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormRow label="Input Schema (JSON)" htmlFor="inputSchema" error={errors.inputSchema}>
                  <textarea name="inputSchema" id="inputSchema" value={commonFormData.inputSchema} onChange={handleCommonChange} rows={4}
                            className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm font-mono bg-white text-neutral-900 placeholder-neutral-500" placeholder='e.g., {"prompt": "string"}' />
                </FormRow>
                <FormRow label="Output Schema (JSON)" htmlFor="outputSchema" error={errors.outputSchema}>
                  <textarea name="outputSchema" id="outputSchema" value={commonFormData.outputSchema} onChange={handleCommonChange} rows={4}
                            className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm font-mono bg-white text-neutral-900 placeholder-neutral-500" placeholder='e.g., {"result": "string"}' />
                </FormRow>
              </div>

              <FormRow label="Compliance" htmlFor="compliance" error={errors.compliance as string}>
                <div className="space-y-2 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-x-4 gap-y-2 pt-1">
                  {COMPONENT_COMPLIANCE_OPTIONS.map(opt => (
                    <label key={opt} className="flex items-center text-sm">
                      <input type="checkbox" name="compliance" value={opt} checked={commonFormData.compliance.includes(opt)} onChange={handleCheckboxChange}
                            className="h-4 w-4 text-primary border-neutral-300 rounded focus:ring-primary mr-2" />
                      {opt}
                    </label>
                  ))}
                </div>
              </FormRow>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormRow label="Cost Tier" htmlFor="costTier" error={errors.costTier}>
                  <select name="costTier" id="costTier" value={commonFormData.costTier} onChange={handleCommonChange}
                          className="w-full px-3 py-2 border border-neutral-300 rounded-md shadow-sm focus:ring-primary focus:border-primary sm:text-sm bg-white text-neutral-900 placeholder-neutral-500">
                    {COMPONENT_COST_TIERS.map(tier => <option key={tier} value={tier!}>{tier}</option>)}
                  </select>
                </FormRow>
                <FormRow label="Visibility" htmlFor="visibility" error={errors.visibility} required>
                  <div className="flex space-x-4 pt-2">
                    {COMPONENT_VISIBILITY_OPTIONS.map(opt => (
                      <label key={opt} className="flex items-center text-sm">
                        <input type="radio" name="visibility" value={opt} checked={commonFormData.visibility === opt} onChange={handleCommonChange}
                              className="h-4 w-4 text-primary border-neutral-300 focus:ring-primary mr-1.5" />
                        {opt}
                      </label>
                    ))}
                  </div>
                </FormRow>
              </div>

              {submissionStatus === 'success' && (
                <div className="p-3 bg-green-50 border border-green-200 rounded-md text-sm text-green-700 flex items-center">
                  <CheckCircleIcon className="w-5 h-5 mr-2"/> Component submitted successfully! Redirecting...
                </div>
              )}
              {submissionStatus === 'error' && Object.keys(errors).length > 0 && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-700 flex items-center">
                  <XCircleIcon className="w-5 h-5 mr-2"/> Please correct the errors above.
                </div>
              )}
              {submissionStatus === 'error' && !Object.keys(errors).length && selectedType && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-700 flex items-center">
                  <XCircleIcon className="w-5 h-5 mr-2"/> Submission failed. Please try again.
                </div>
              )}

              <div className="pt-4 flex justify-end space-x-3">
                <Button type="button" variant="ghost" onClick={() => navigate(-1)}>Cancel</Button>
                <Button type="submit" variant="primary" leftIcon={<UploadIcon className="w-4 h-4" />} isLoading={submissionStatus === 'success'}>
                  Submit Component
                </Button>
              </div>
            </>
          )}
        </form>
      </Card>
      <ChatAssistant selectedComponentType={selectedType || null} currentComponentData={currentFullComponentData} />
    </div>
  );
};

export default SubmitComponentPage;