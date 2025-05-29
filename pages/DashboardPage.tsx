
import React from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { DUMMY_COMPONENTS_PRESET, DUMMY_WORKFLOWS, DUMMY_SYSTEM_STATUS } from '../constants';
import { PlusIcon, StarIcon, PlayIcon, CheckCircleIcon, ExclamationTriangleIcon, InformationCircleIcon } from '../icons';
import { Link } from 'react-router-dom';
import { AIComponent, Workflow, SystemStatus } from '../types';


const PersonalizedFeedCard: React.FC<{ item: AIComponent | Workflow }> = ({ item }) => {
  const isComponent = 'type' in item; // Type guard
  const linkTo = isComponent ? `/marketplace/component/${item.id}` : `/builder/${item.id}`;
  
  let iconDisplay: React.ReactNode;
  if (item.icon && React.isValidElement(item.icon)) {
    iconDisplay = React.cloneElement(item.icon as React.ReactElement<React.SVGProps<SVGSVGElement>>, { className: "w-6 h-6 text-primary" });
  } else {
    iconDisplay = <PlayIcon className="w-6 h-6 text-primary" />;
  }

  return (
    <Card className="hover:shadow-primary/30">
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0 w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
           {iconDisplay}
        </div>
        <div>
          <Link to={linkTo} className="text-lg font-semibold text-neutral-800 hover:text-primary line-clamp-1">{item.name}</Link>
          <p className="text-sm text-neutral-600 mt-1 line-clamp-2">{item.description}</p>
          {isComponent && <span className="mt-2 inline-block bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full text-xs font-medium">{(item as AIComponent).type}</span>}
          {!isComponent && (item as Workflow).status && <span className="mt-2 inline-block bg-green-100 text-green-700 px-2 py-0.5 rounded-full text-xs font-medium">{(item as Workflow).status}</span>}
        </div>
      </div>
    </Card>
  );
};

const SystemHealthItem: React.FC<{ item: SystemStatus }> = ({ item }) => {
  let IconComponent;
  let iconColorClass;

  switch (item.status) {
    case 'OK':
      IconComponent = CheckCircleIcon;
      iconColorClass = 'text-status-success';
      break;
    case 'Warning':
      IconComponent = ExclamationTriangleIcon;
      iconColorClass = 'text-status-warning';
      break;
    case 'Error':
      IconComponent = ExclamationTriangleIcon; // Could use a different one like XCircleIcon
      iconColorClass = 'text-status-error';
      break;
    default:
      IconComponent = InformationCircleIcon;
      iconColorClass = 'text-neutral-500';
  }

  return (
    <div className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center space-x-2">
        <IconComponent className={`w-5 h-5 ${iconColorClass}`} />
        <span className="text-sm font-medium text-neutral-700">{item.serviceName}</span>
      </div>
      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
        item.status === 'OK' ? 'bg-green-100 text-green-700' : 
        item.status === 'Warning' ? 'bg-yellow-100 text-yellow-700' : 
        'bg-red-100 text-red-700'
      }`}>
        {item.status}
      </span>
    </div>
  );
};


const DashboardPage: React.FC = () => {
  const recommendedComponents = DUMMY_COMPONENTS_PRESET.slice(0, 2);
  const trendingWorkflows = DUMMY_WORKFLOWS.slice(0, 2);

  return (
    <div className="space-y-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-neutral-800">Welcome to your AI Ops Dashboard</h1>
        <p className="text-neutral-600 mt-1">Here's what's happening in your AI ecosystem.</p>
      </header>

      {/* Quick Access Toolbar */}
      <Card title="Quick Actions" className="mb-8">
        <div className="flex space-x-4">
          <Button variant="primary" leftIcon={<PlusIcon className="w-4 h-4" />}>
            New Workflow
          </Button>
          <Button variant="secondary" leftIcon={<StarIcon className="w-4 h-4" />}>
            Starred Items
          </Button>
          <Button variant="outline" leftIcon={<PlayIcon className="w-4 h-4" />}>
            Recent Runs
          </Button>
        </div>
      </Card>
      
      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Personalized Feed Column */}
        <div className="lg:col-span-2 space-y-6">
          <Card title="Recommended Components">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendedComponents.map(item => <PersonalizedFeedCard key={item.id} item={item} />)}
            </div>
          </Card>
          <Card title="Trending Workflows">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {trendingWorkflows.map(item => <PersonalizedFeedCard key={item.id} item={item} />)}
            </div>
          </Card>
        </div>

        {/* System Health Monitor Column */}
        <div className="lg:col-span-1 space-y-6">
          <Card title="System Health">
            <div className="space-y-3">
              {DUMMY_SYSTEM_STATUS.map(status => <SystemHealthItem key={status.serviceName} item={status} />)}
            </div>
          </Card>
          <Card title="Recent Activity">
            <ul className="space-y-3 text-sm">
              <li className="text-neutral-600 hover:text-primary cursor-pointer">You edited "Data Ingest v2"</li>
              <li className="text-neutral-600 hover:text-primary cursor-pointer">Jane commented on "LLM Summarizer"</li>
              <li className="text-neutral-600 hover:text-primary cursor-pointer">Deployment of "Image Classifier v1.1" succeeded</li>
            </ul>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;