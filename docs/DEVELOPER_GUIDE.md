# AI Ops Console Developer Guide

## 1. Project Overview

### 1.1 Architecture

The AI Ops Console is a modern web application built with:

- **Frontend**: React + TypeScript + Material-UI
- **Backend**: FastAPI + PostgreSQL
- **Authentication**: JWT-based
- **AI Integration**: Gemini API
- **State Management**: React Context

### 1.2 Key Features

1. **Component Management**
   - Submit and manage AI components
   - Version control
   - Dependency management

2. **Workflow Builder**
   - Visual workflow creation
   - Component chaining
   - Execution monitoring

3. **AI Integration**
   - Gemini API integration
   - Prompt engineering
   - Response handling

### 1.3 New Architecture & Features (2024)

The following features and architectural changes have been added:

- **Recommendation System**: Backend service and API for personalized recommendations, with analytics and frontend integration.
- **Notification System**: Real-time notifications, notification center, analytics dashboard, and user preferences.
- **Real-Time Updates**: WebSocket-based updates for workflows, notifications, and metrics.
- **Performance Monitoring**: Prometheus-based backend metrics, frontend Web Vitals, service worker for offline support.
- **Workflow Templates**: CRUD, versioning, stats, and search for reusable workflow templates.

See `ARCHITECTURE.md` and `architecture/testing_and_contribution.md` for detailed diagrams and flow.

## 2. Development Environment

### 2.1 Prerequisites

#### Frontend
- Node.js (v18 or later)
- npm (v9 or later)
- TypeScript (v5 or later)
- React (v18 or later)
- Material-UI (v5 or later)

#### Backend
- Python (v3.11 or later)
- FastAPI
- PostgreSQL (v15 or later)
- Redis (v7 or later)
- uvicorn

#### Development Tools
- VS Code
- Git
- Docker (optional)
- Postman (API testing)

### 2.2 Project Setup

#### Frontend Setup
```bash
cd mcp_project_frontend
npm install
npm start
```

#### Backend Setup
```bash
cd mcp_project_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Environment Variables
```bash
# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GEMINI_API_KEY=your_key_here

# Backend
DATABASE_URL=postgresql://user:password@localhost:5432/mcp_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your_secret_key
JWT_EXPIRE_MINUTES=30
```

## 2.3 Developer Onboarding

1. **Clone the repository**
2. **Setup environment** (see above)
3. **Read `DOCUMENTATION_STRUCTURE.md` for doc organization**
4. **Read `architecture/testing_and_contribution.md` for code/test standards**
5. **Start with a small issue or feature**
6. **Create a feature branch**
7. **Write code and tests**
8. **Open a Pull Request (PR)**
9. **Request review and address feedback**
10. **Update documentation as needed**

## 3. Development Workflow

### 3.1 Git Workflow

1. **Branching Strategy**
   - `main`: Production code
   - `develop`: Development code
   - `feature/*`: New features
   - `hotfix/*`: Critical fixes
   - `release/*`: Release preparation

2. **Commit Messages**
   ```
   feat: Add new feature
   fix: Fix bug
   docs: Update documentation
   style: Code style changes
   refactor: Code refactoring
   test: Add tests
   chore: Maintenance
   ```

### 3.2 Code Review

1. **Checklist**
   - Code style
   - Type safety
   - Error handling
   - Testing
   - Documentation
   - Security

2. **Review Process**
   - Self-review
   - Peer review
   - Merge approval
   - CI/CD checks

### 3.3 Contribution Workflow (2024)

- **Branching**: Use `feature/`, `bugfix/`, `hotfix/`, `release/` prefixes
- **Commits**: Conventional commits (`feat:`, `fix:`, `docs:`, etc.)
- **Pull Requests**: PRs must reference checklist items and include test results
- **Code Review**: Peer review required, use review checklist (see `architecture/testing_and_contribution.md`)
- **CI/CD**: All PRs must pass CI (tests, lint, coverage)
- **Documentation**: Update docs for all new features/changes

## 4. Code Style

### 4.1 TypeScript

1. **Type Safety**
   - Use strict mode
   - Define interfaces
   - Use enums
   - Avoid any

2. **Naming Conventions**
   - PascalCase for components
   - camelCase for functions
   - UPPER_CASE for constants
   - kebab-case for files

### 4.2 React

1. **Component Structure**
   ```typescript
   // Component structure
   interface Props {
     // Props
   }

   const Component: React.FC<Props> = ({ props }) => {
     // State
     // Effects
     // Functions
     return (
       // JSX
     );
   };
   ```

2. **State Management**
   - Use Context API
   - Keep state minimal
   - Use proper hooks
   - Handle errors

### 4.3 Code Standards (2024)

- **TypeScript/React**: Strict mode, interfaces for props, enums for fixed values, error boundaries, memoization, accessibility, path aliases, generics, type guards, readonly types, union types, functional components, hooks, context, composition (see `instructions.md`)
- **Python/FastAPI**: Pydantic for validation, dependency injection, transactions, async/await, type hints, error handling, API versioning, OpenAPI docs
- **General**: Modular code, clear separation, reusable components, maintainable code, JSDoc/docstrings, update docs with code

## 5. Testing

### 5.1 Test Types

1. **Unit Tests**
   - Test functions
   - Validate logic
   - Check edge cases

2. **Integration Tests**
   - Test components
   - Validate workflows
   - Check dependencies

3. **E2E Tests**
   - Test full flow
   - Validate UI
   - Check error handling

### 5.2 Testing Frameworks

1. **Frontend**
   - Jest
   - React Testing Library
   - Cypress

2. **Backend**
   - pytest
   - FastAPI TestClient
   - pytest-asyncio

## 6. Documentation

### 6.1 Documentation Types

1. **Technical Docs**
   - API documentation
   - Component docs
   - Architecture docs
   - Error handling

2. **Developer Docs**
   - Setup guide
   - Workflow
   - Best practices
   - Troubleshooting

3. **User Docs**
   - Usage guide
   - Component guide
   - Workflow guide
   - Troubleshooting

### 6.2 Documentation Standards & Review

- All public APIs, components, and services must be documented
- Follow structure in `DOCUMENTATION_STRUCTURE.md`
- Update docs with each major change
- All doc changes must be reviewed for accuracy and clarity
- Use diagrams and examples where helpful
- Reference user and developer guides in PRs

## 7. Deployment

### 7.1 Deployment Process

1. **Frontend**
   - Build assets
   - Deploy to CDN
   - Update config
   - Monitor

2. **Backend**
   - Build container
   - Deploy to cluster
   - Update config
   - Monitor

### 7.2 CI/CD Pipeline

1. **Build**
   - Run tests
   - Build assets
   - Build container

2. **Deploy**
   - Deploy frontend
   - Deploy backend
   - Update config
   - Monitor

## 8. Troubleshooting

### 8.1 Common Issues

1. **Frontend**
   - Build errors
   - Type errors
   - Styling issues
   - Performance

2. **Backend**
   - Database errors
   - API errors
   - Authentication
   - Performance

### 8.2 Debugging Tools

1. **Frontend**
   - React DevTools
   - Chrome DevTools
   - Performance monitoring

2. **Backend**
   - Python debugger
   - Logging
   - Performance monitoring

## 9. Resources

### 9.1 Learning Resources

1. **React**
   - React documentation
   - TypeScript documentation
   - Material-UI documentation

2. **FastAPI**
   - FastAPI documentation
   - Python documentation
   - PostgreSQL documentation

### 9.2 Development Tools

1. **Code Editors**
   - VS Code
   - Extensions
   - Settings

2. **Development Tools**
   - Git
   - Docker
   - Postman
   - Chrome DevTools

## 10. Best Practices

### 10.1 Code Quality

1. **Type Safety**
   - Use TypeScript
   - Define interfaces
   - Use enums
   - Avoid any

2. **Error Handling**
   - Handle errors
   - Use error boundaries
   - Log errors
   - Provide feedback

3. **Performance**
   - Optimize code
   - Use memoization
   - Implement caching
   - Monitor performance

### 10.2 Security

1. **Authentication**
   - Use JWT
   - Validate tokens
   - Handle sessions
   - Secure storage

2. **Data Protection**
   - Encrypt data
   - Use secure storage
   - Implement access control
   - Follow compliance

## 11. Contributing

### 11.1 Guidelines

1. **Code Style**
   - Follow guidelines
   - Use TypeScript
   - Write tests
   - Document code

2. **Testing**
   - Write tests
   - Run tests
   - Fix issues
   - Document tests

3. **Documentation**
   - Update docs
   - Add examples
   - Fix errors
   - Improve clarity

## 12. Version Control

### 12.1 Versioning

1. **Semantic Versioning**
   - MAJOR.MINOR.PATCH
   - Breaking changes
   - New features
   - Bug fixes

2. **Branch Management**
   - Feature branches
   - Hotfix branches
   - Release branches
   - Main branch

## 13. Security

### 13.1 Security Considerations

1. **Authentication**
   - Use JWT
   - Validate tokens
   - Handle sessions
   - Secure storage

2. **Data Protection**
   - Encrypt data
   - Use secure storage
   - Implement access control
   - Follow compliance

### 13.2 Security Best Practices

1. **Code Security**
   - Validate inputs
   - Handle errors
   - Use secure libraries
   - Follow security guidelines

2. **Data Security**
   - Encrypt data
   - Use secure storage
   - Implement access control
   - Follow compliance

## 14. Performance

### 14.1 Performance Considerations

1. **Frontend**
   - Optimize code
   - Use memoization
   - Implement caching
   - Monitor performance

2. **Backend**
   - Optimize queries
   - Use caching
   - Monitor performance
   - Scale resources

### 14.2 Performance Best Practices

1. **Code Optimization**
   - Optimize code
   - Use proper algorithms
   - Implement caching
   - Monitor performance

2. **Resource Management**
   - Use proper resources
   - Implement caching
   - Monitor usage
   - Scale resources

## 15. Monitoring

### 15.1 Monitoring Requirements

1. **Frontend**
   - Performance monitoring
   - Error tracking
   - User behavior
   - Resource usage

2. **Backend**
   - Performance monitoring
   - Error tracking
   - Resource usage
   - System health

### 15.2 Monitoring Tools

1. **Frontend**
   - Performance monitoring
   - Error tracking
   - Analytics
   - User behavior

2. **Backend**
   - Performance monitoring
   - Error tracking
   - Resource usage
   - System health

## 16. Maintenance

### 16.1 Regular Tasks

1. **Code Updates**
   - Update dependencies
   - Fix bugs
   - Improve performance
   - Add features

2. **Documentation Updates**
   - Update guides
   - Add examples
   - Fix errors
   - Improve clarity

### 16.2 Security Updates

1. **Dependency Updates**
   - Update dependencies
   - Fix vulnerabilities
   - Follow security guidelines
   - Monitor security

2. **Code Security**
   - Update code
   - Fix vulnerabilities
   - Follow security guidelines
   - Monitor security

## 17. Support

### 17.1 Support Resources

1. **Documentation**
   - Technical documentation
   - Developer documentation
   - User documentation
   - Troubleshooting guides

2. **Community**
   - GitHub issues
   - Discussion forums
   - Slack channels
   - Support tickets

### 17.2 Support Guidelines

1. **Issue Reporting**
   - Provide details
   - Include steps
   - Add logs
   - Follow guidelines

2. **Support Response**
   - Provide help
   - Follow guidelines
   - Document solutions
   - Improve documentation

## 18. Future Development

### 18.1 Planned Features

1. **New Features**
   - Planned features
   - Development timeline
   - Resource requirements
   - Testing requirements

2. **Improvements**
   - Code improvements
   - Performance improvements
   - Security improvements
   - Documentation improvements

### 18.2 Development Roadmap

1. **Short Term**
   - Immediate tasks
   - Resource requirements
   - Development timeline
   - Testing requirements

2. **Long Term**
   - Future plans
   - Resource requirements
   - Development timeline
   - Testing requirements

## Development Workflow

### Type System

The project uses a centralized type system defined in `src/types/analytics.ts`. Key types include:

- `Alert`: Represents system alerts with severity levels and metadata
- `NotificationGroup`: Groups related alerts for better organization
- `AnalyticsEvent`: Tracks system events and metrics
- `UserBehavior`: Captures user interactions and actions

### Notification System

The notification system consists of several services:

1. **AlertNotificationService**: Core service for managing alerts
2. **NotificationFilterService**: Handles alert filtering and grouping
3. **NotificationSoundService**: Manages notification sounds
4. **EmailNotificationService**: Handles email notifications
5. **PushNotificationService**: Manages push notifications
6. **NotificationAnalyticsService**: Tracks notification metrics

### Code Organization

- `src/components/`: React components
- `src/contexts/`: React contexts
- `src/services/`: Service classes
- `src/types/`: TypeScript type definitions
- `src/utils/`: Utility functions
- `src/hooks/`: Custom React hooks

## Code Style

### TypeScript

- Use strict type checking
- Prefer interfaces over type aliases
- Use proper type imports/exports
- Document complex types

### React

- Use functional components with hooks
- Follow React best practices
- Implement proper error boundaries
- Use proper prop types

### Testing

- Write unit tests for services
- Test React components
- Use proper mocking
- Follow testing best practices

## Documentation

### Code Documentation

- Use JSDoc comments
- Document complex functions
- Keep documentation up to date
- Use proper markdown formatting

### API Documentation

- Document API endpoints
- Use OpenAPI/Swagger
- Keep API docs current
- Include examples

## Deployment

### Frontend Deployment

```bash
cd mcp_project_frontend
npm run build
```

### Backend Deployment

```bash
cd mcp_project_backend
gunicorn main:app
```

## Troubleshooting

### Common Issues

1. Type errors
2. Build failures
3. Test failures
4. Runtime errors

### Solutions

1. Check type definitions
2. Verify imports
3. Check dependencies
4. Review error logs

## Resources

### Documentation

- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Material-UI Documentation](https://mui.com/getting-started/usage/)

### Tools

- [VS Code](https://code.visualstudio.com/)
- [Postman](https://www.postman.com/)
- [pgAdmin](https://www.pgadmin.org/)
- [Redis Commander](https://github.com/joeferner/redis-commander)
