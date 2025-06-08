import React, { useState } from 'react';

const guides = [
  {
    title: 'User Guide',
    file: '/docs/USER_GUIDE.md',
    description: 'Overview, settings, notifications, privacy, troubleshooting, FAQ, and feedback.'
  },
  {
    title: 'Workflow Builder Guide',
    file: '/docs/user_guides/workflow_builder_guide.md',
    description: 'How to create, manage, and optimize workflows.'
  },
  {
    title: 'Component Submission Guide',
    file: '/docs/user_guides/component_submission_guide.md',
    description: 'How to submit, validate, and manage custom components.'
  },
  {
    title: 'Authentication Guide',
    file: '/docs/user_guides/authentication_guide.md',
    description: 'Login, API keys, session management, and security.'
  },
  {
    title: 'Deployment Guide',
    file: '/docs/user_guides/deployment_guide.md',
    description: 'Deployment, backup, recovery, and maintenance.'
  },
  {
    title: 'Troubleshooting Guide',
    file: '/docs/user_guides/troubleshooting_guide.md',
    description: 'Common issues, debugging, performance, and support.'
  },
];

export const HelpPage: React.FC = () => {
  const [search, setSearch] = useState('');
  const filtered = guides.filter(g =>
    g.title.toLowerCase().includes(search.toLowerCase()) ||
    g.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-3xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Help & Support</h1>
      <input
        type="text"
        placeholder="Search help topics..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        className="w-full border rounded px-3 py-2 mb-6"
        aria-label="Search help topics"
      />
      <div className="space-y-6">
        {filtered.map(g => (
          <div key={g.title} className="bg-white dark:bg-neutral-900 rounded shadow p-4">
            <h2 className="text-xl font-semibold mb-1">{g.title}</h2>
            <p className="mb-2 text-neutral-600 dark:text-neutral-300">{g.description}</p>
            <a
              href={g.file}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              View Guide
            </a>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="text-neutral-500 text-center">No help topics found.</div>
        )}
      </div>
      <div className="mt-10 border-t pt-6">
        <h2 className="text-lg font-semibold mb-2">Need more help?</h2>
        <ul className="list-disc pl-6 text-neutral-700 dark:text-neutral-200">
          <li>Contact support via the feedback form in settings</li>
          <li>Report bugs or request features via GitHub Issues</li>
          <li>Join the community forum or Slack for peer support</li>
        </ul>
      </div>
    </div>
  );
};

export default HelpPage; 