# PHASE 2: CORE FUNCTIONALITY CHECKLIST (�� High Priority)

## Phase 2 Core Starter Structure: COMPLETE

- [x] Created `services` directory in `mcp/api`
- [x] Created `tests` directory in `mcp/api`
- [x] Implemented stubs for `auth_service.py`, `data_service.py`, `data_visualization_service.py`
- [x] Added `data_visualization.html` and `index.html`
- [x] Updated `mcp/db/models/mcp.py` for `visualization_metadata`
- [x] Added `test_auth_service.py`
- [x] Updated routers to delegate to new services (where applicable)
- [x] Created devlog entry

---

## 2.1 Complete Workflow Builder Implementation

### UI/Frontend

- [ ] Integrate React Flow for the workflow canvas
  - [ ] Set up React Flow with custom node and edge types
  - [ ] Implement zoom, pan, and fit-to-view controls
- [ ] Implement drag-and-drop for components from palette to canvas
  - [ ] Enable drag from palette, drop to canvas, and node creation
  - [ ] Support drag-to-reorder and drag-to-connect
- [ ] Add component palette
  - [ ] Display all available MCP components
  - [ ] Implement search and filter for palette
  - [ ] Show component details on hover/click
- [ ] Create properties panel for node configuration
  - [ ] Display config form for selected node (dynamic by type)
  - [ ] Support validation and error display
  - [ ] Allow editing of all config fields, including advanced options
- [ ] Implement workflow validation logic
  - [ ] Validate required fields for all nodes
  - [ ] Validate connections (no cycles, valid data flow)
  - [ ] Show validation errors inline and in a summary
- [ ] Add save/load workflow functionality
  - [ ] Serialize workflow to backend (API)
  - [ ] Load workflow from backend (API)
  - [ ] Support local draft saving (optional)
- [ ] Implement workflow versioning
  - [ ] Allow users to create new versions
  - [ ] Show version history and allow rollback
- [ ] Add workflow templates
  - [ ] Provide built-in templates for common workflows
  - [ ] Allow users to save custom templates

### Backend

- [ ] Implement/extend workflow definition service for versioning and templates
- [ ] Add endpoints for workflow CRUD, versioning, and template management
- [ ] Ensure all workflow data is validated and persisted correctly

### Acceptance Criteria

- Users can visually build, save, load, and version workflows with validation and templates.

---

## 2.2 Advanced Code Editor Integration

### UI/Frontend

- [ ] Replace all code textareas with Monaco Editor
  - [ ] Integrate Monaco Editor in all relevant forms/pages
  - [ ] Support multiple languages (Python, TypeScript, SQL, etc.)
- [ ] Add syntax highlighting for all supported languages
- [ ] Implement code validation and linting
  - [ ] Show errors/warnings inline
  - [ ] Support custom linting rules for MCP scripts
- [ ] Add auto-completion and IntelliSense
  - [ ] Provide language server integration if possible
  - [ ] Support code snippets and templates
- [ ] Implement code formatting (auto-format on save)
- [ ] Add file upload capabilities for code/scripts
  - [ ] Support drag-and-drop and file picker
  - [ ] Parse and display uploaded code in editor
- [ ] Create code templates and snippets for common tasks

### Backend

- [ ] Ensure backend supports storing and retrieving code files/scripts
- [ ] Add endpoints for code validation/linting if needed

### Acceptance Criteria

- Users have a professional code editing experience with validation, completion, and file support.

---

## 2.3 Real-time Updates with WebSocket

### Backend

- [ ] Implement WebSocket server for real-time updates
  - [ ] Set up FastAPI WebSocket endpoints
  - [ ] Integrate with workflow execution engine for status streaming
  - [ ] Implement pub/sub or event bus for backend events
- [ ] Add workflow execution status streaming
  - [ ] Stream step status, logs, and results in real time
- [ ] Implement real-time notifications
  - [ ] Notify users of workflow events, errors, completions
- [ ] Add collaborative editing capabilities (optional/advanced)
  - [ ] Support multiple users editing the same workflow
  - [ ] Implement conflict resolution and presence indicators
- [ ] Create connection management and reconnection logic
  - [ ] Handle dropped connections, retries, and user feedback
- [ ] Add real-time dashboard updates
  - [ ] Push system status, metrics, and activity to dashboard clients

### Frontend

- [ ] Implement WebSocket client hooks and context
  - [ ] Create `useWebSocket` hook for connection management
  - [ ] Provide context for WebSocket data/events
- [ ] Integrate real-time updates into workflow builder, dashboard, and notifications

### Acceptance Criteria

- Users see real-time updates for workflow execution, dashboard, and notifications. Multiple users can collaborate (if implemented).

---

## 2.4 Comprehensive Testing Suite

### Frontend

- [ ] Set up Jest and React Testing Library
- [ ] Add unit tests for all React components
- [ ] Implement integration tests for user flows (e.g., workflow creation, code editing)
- [ ] Add end-to-end tests with Playwright
  - [ ] Write E2E tests for critical flows (login, workflow build, run, monitor)
- [ ] Create test data factories for frontend

### Backend

- [ ] Expand backend test suite (pytest)
- [ ] Add unit tests for all core services and routers
- [ ] Implement integration tests for API endpoints
- [ ] Add performance testing (e.g., with Locust)
- [ ] Implement visual regression testing (if applicable)
- [ ] Set up CI/CD pipeline with automated testing
  - [ ] Add GitHub Actions workflow for tests

### Acceptance Criteria

- 80%+ code coverage, all critical flows tested, tests run automatically on CI/CD.

---

## 2.5 Proper State Management with Persistence

### Frontend

- [ ] Implement Zustand stores for complex state (workflows, user data, etc.)
- [ ] Add state persistence (localStorage, IndexedDB, or backend)
  - [ ] Serialize/deserialize state with versioning
- [ ] Implement optimistic updates for UI responsiveness
- [ ] Add state synchronization across browser tabs
  - [ ] Use BroadcastChannel or similar
- [ ] Create state migration strategies for breaking changes
- [ ] Add state debugging tools (Redux DevTools, custom logger)

### Acceptance Criteria

- State is robust, persistent, synchronized, and debuggable.
