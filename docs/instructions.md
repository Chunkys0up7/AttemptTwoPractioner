# Project Implementation Instructions

## Workflow Guidelines

First task is to check the current code status and ensure no duplication or changes that are not aligned with the project goals and technology

1. Always work from a checklist and complete tasks in order
2. Once a task is complete:
   - Check the code in
   - Push to remote repository
   - Update the devlog with the changes
   - Ensure documentation reflects the changes
3. Add all additional tasks and problem resolutions to the checklist
4. Follow the implementation order:
   - Phase 1: Critical Security & Stability
   - Phase 2: Core Functionality & Performance
   - Phase 3: User Experience & Analytics
   - Phase 4: Enhancements & Polish
5. Ensure Checklists are updated and removed when complete
6. Resolve all code problems fully when they appear
7. Maintain project structure and do not delete files or folders without asking - always update devlog with what file was deleted and when

## Project Phases

1. Phase 1: Initial Setup & Planning
   - ✅ Project structure established
   - ✅ TypeScript configuration
   - ✅ Initial component architecture

2. Phase 2: Core Functionality & Performance
   - ✅ Component system implementation
   - ✅ Workflow builder foundation
   - ✅ Backend API integration
   - ✅ Type safety improvements

3. Phase 3: User Experience & Analytics
   - ✅ Component palette UI
   - ✅ Search and filtering
   - ✅ Error handling
   - ✅ Loading states

4. Phase 4: Enhancements & Polish
   - 🔍 Performance optimization
   - 🔍 Advanced analytics
   - 🔍 Additional component types
   - 🔍 Documentation improvements

## General Guidelines

### Project Structure
- Never delete files or folders without explicit approval
- Always update devlog with any structural changes
- Maintain clear separation between frontend and backend code
- Follow the established directory structure:
  ```
  mcp_project_frontend/
  ├── src/
  │   ├── components/
  │   │   ├── common/      # Reusable UI components
  │   │   ├── marketplace/ # Component marketplace
  │   │   └── workflow/    # Workflow builder
  │   ├── hooks/          # Custom React hooks
  │   │   ├── workflow/   # Workflow management
  │   │   ├── components/ # Component management
  │   │   └── utils/      # Utility hooks
  │   ├── context/        # React Context providers
  │   ├── types/          # TypeScript types
  │   └── utils/          # Utility functions
  ```

  ```
  mcp_project_backend/
  ├── mcp/
  │   ├── api/           # API routes and schemas
  │   ├── components/     # Component management
  │   ├── core/          # Core services
  │   ├── db/           # Database models and CRUD
  │   ├── schemas/      # Pydantic schemas
  │   └── utils/        # Utility functions
  ```

### Code Standards

#### TypeScript
- ✅ Use strict mode
- ✅ Always use interfaces for component props
- ✅ Use enums for fixed sets of values
- ✅ Implement proper error handling
- ✅ Use TypeScript path aliases for imports
- ✅ Follow the existing type structure in `types/`
- ✅ Use proper generics for collections
- ✅ Implement proper type guards
- ✅ Use readonly types for immutable data
- ✅ Use proper union types for variant data

#### React
- ✅ Use functional components with hooks
- ✅ Implement proper error boundaries
- ✅ Use memoization for performance
- ✅ Follow accessibility guidelines
- ✅ Maintain consistent prop types
- ✅ Use proper event handlers
- ✅ Implement proper context usage
- ✅ Use proper component composition

#### Backend
- ✅ Use Pydantic for data validation
- ✅ Implement proper dependency injection
- ✅ Use proper database transactions
- ✅ Implement proper error handling
- ✅ Use proper logging
- ✅ Implement proper security measures
- ✅ Use proper caching mechanisms
- ✅ Implement proper rate limiting

#### React
- Use functional components with hooks
- Implement proper error boundaries
- Use memoization for performance
- Follow accessibility guidelines
- Maintain consistent prop types

#### State Management
- Use Redux for global state
- Implement proper action creators
- Use selectors for state access
- Maintain proper reducer structure

### Development Process
- Always update devlog with:
  - Completed tasks
  - Changes made
  - Next steps
  - Technical decisions
  - Testing status
  - Structural changes
  - Code improvements

- Documentation requirements:
  - API endpoints
  - Security measures
  - Component architecture
  - State management
  - Error handling
  - Performance optimizations

### Testing Requirements
- Unit tests for all components
- Integration tests for workflows
- E2E tests for critical paths
- Performance benchmarks
- Accessibility testing

### Error Handling
- Implement proper error boundaries
- Add retry mechanisms
- Log errors appropriately
- Provide user-friendly error messages
- Implement loading states

### Performance Optimization
- Use memoization
- Implement proper caching
- Optimize component rendering
- Use code splitting
- Implement lazy loading

### Accessibility
- Use proper ARIA labels
- Implement keyboard navigation
- Add focus management
- Ensure proper color contrast
- Follow WCAG guidelines

### Security
- Implement proper input validation
- Use secure API endpoints
- Implement proper authentication
- Follow security best practices
- Regular security audits

## Documentation Requirements

1. Keep the devlog updated with:
   - Completed tasks
   - Changes made
   - Next steps
   - Technical decisions
   - Testing status
   - Structural changes
   - Code improvements

2. Maintain documentation for:
   - API endpoints
   - Security measures
   - Component architecture
   - State management
   - Error handling
   - Performance optimizations
   - Accessibility features

## Code Review Checklist

### TypeScript
- [ ] Proper type definitions
- [ ] Interface usage
- [ ] Error handling
- [ ] Performance considerations

### React
- [ ] Proper component structure
- [ ] Error boundaries
- [ ] Accessibility
- [ ] Performance optimization

### State Management
- [ ] Proper Redux usage
- [ ] Action creators
- [ ] Selectors
- [ ] Reducer structure

### Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests
- [ ] Performance tests

### Security
- [ ] Input validation
- [ ] API security
- [ ] Authentication
- [ ] Security measures

### Performance
- [ ] Memoization
- [ ] Caching
- [ ] Code splitting
- [ ] Lazy loading

### Accessibility
- [ ] ARIA labels
- [ ] Keyboard navigation
- [ ] Focus management
- [ ] WCAG compliance

## Project Structure Preservation

### Frontend Structure
- Maintain `mcp_project_frontend` directory
- Keep component organization
- Preserve type definitions
- Maintain hook structure
- Keep utility functions organized

### Backend Structure
- Maintain `mcp_project_backend` directory
- Keep API structure
- Preserve database schema
- Maintain security measures

### Documentation Structure
- Keep architecture documentation
- Maintain API documentation
- Preserve security documentation
- Keep testing documentation

## Change Management

### Before any major changes:
- Update devlog
- Document technical decisions
- Review impact on existing code
- Plan testing strategy
- Consider security implications

### After changes:
- Update documentation
- Run tests
- Verify performance
- Check security
- Update devlog

## Technical Decisions Log

- Date: 2025-06-06
- Changes:
  - Implemented Redux for state management
  - Added proper error handling
  - Enhanced TypeScript types
  - Migrated to Vite build system
  - Fixed module resolution issues
  - Standardized import paths using @ alias
  - Updated TypeScript configuration for better module resolution
  - Improved type definitions and exports
  - Fixed icon component imports and exports
  - Updated hooks implementation and exports
  - Enhanced component structure and organization
  - Improved accessibility
  - Added performance optimizations
- Technical Decisions:
  - Using Redux Toolkit for state management
  - Implementing proper error boundaries
  - Using TypeScript path aliases
  - Following React best practices
  - Implementing accessibility standards
- Impact:
  - Improved code maintainability
  - Better error handling
  - Enhanced performance
  - Better accessibility
  - More reliable state management

## Next Steps

1. Implement remaining state management features
2. Add more comprehensive testing
3. Enhance error handling
4. Improve performance optimizations
5. Add more accessibility features
6. Document all changes
7. Review security measures
8. Update devlog with progress

## Important Notes

- Always consult documentation before making changes
- Follow established patterns and conventions
- Maintain consistent code style
- Keep documentation up to date
- Follow security best practices
- Regular code reviews required
- Performance testing mandatory
- Accessibility testing required
- Security audits recommended

## Testing Requirements

1. Write tests for all new features
2. Include:
   - Unit tests
   - Integration tests
   - Security tests
   - Performance tests
   - User acceptance tests

## Code Quality Standards

1. Follow coding standards
2. Include proper error handling
3. Add appropriate logging
4. Document code changes
5. Review code before committing

## Security Guidelines

1. Follow security best practices
2. Implement proper authentication
3. Use secure configuration
4. Add input validation
5. Implement error handling

