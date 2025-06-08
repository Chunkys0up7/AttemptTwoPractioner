# Frontend Phase 2 Implementation Plan (Code-Driven)

> **Note:** This checklist is based on a deep dive into the actual codebase as of 2024-06-07. Items below reflect what is truly implemented and what remains. Backend work is complete. See `PHASE_2_CORE_FUNCTIONALITY_CHECKLIST.md` for backend status.

---

## ✅ Fully Implemented (Frontend)
- Monaco Editor is fully integrated as a reusable `CodeEditor` component
- All code/script editing areas use the Monaco-based editor
- Multi-language support (Python, TypeScript, SQL, Markdown, YAML, etc.)
- Syntax highlighting for all supported languages
- Validation/linting (inline errors/warnings, custom validation)
- Auto-completion and code snippets/templates (via `snippets` prop)
- Auto-format on save (for Monaco-supported languages)
- File upload (drag-and-drop and file picker) for code/scripts
- React Flow workflow builder is integrated with drag-and-drop, node/edge state, zoom/pan/fit controls
- Component palette and properties panel are present
- Mobile view handling is present
- Workflow validation logic exists (nodes/edges/structure)
- Documentation and devlog are up to date for these features

---

## 🚧 Remaining Frontend Work (Actionable Checklist)

### A. Workflow Builder
- [x] **Implement workflow versioning UI**
  - [x] Add UI to create new workflow versions *(Save as New Version modal implemented, API integrated, tested, and documented)*
  - [x] Show version history and allow rollback to previous versions *(Restore Version feature implemented, tested, and documented)*
  - [x] Integrate with backend versioning endpoints *(All API integration, error handling, and data flows are robust, tested, and documented)*

### B. Workflow Templates (MarketplacePage)
- [x] **Implement workflow templates UI in MarketplacePage**
  - [x] Browse available workflow templates (list from /api/templates)
  - [x] Filter/search templates by category, name, or public/private
  - [x] Preview template details and versions (modal, accessible, tested)
  - [x] Instantiate a workflow from a selected template (navigates to builder with content)
  - [x] Handle loading, error, and empty states
  - [x] Document and test all features

### C. Code Editor
- [x] **Add UI for browsing/inserting code templates/snippets**
  - [x] Provide a button/menu to insert snippets/templates (implemented in CodeEditor, accessible, documented)
- [x] Ensure snippet/template insertion works in all code/script editing areas
- [x] Support multi-language snippets (Python, TypeScript, SQL, etc.)
- [x] Document and test all features
- [x] **Integrate language server for advanced IntelliSense** (optional/advanced)
  - [x] Add support for external language servers (e.g., Python, via Monaco extensions)
- [x] **Integrate custom formatters for non-Monaco languages**
  - [x] Add Black for Python, Prettier for JS/TS, etc. (if needed)
- [ ] **Expand custom linting rules for MCP scripts**
  - [ ] Add more rules or UI for MCP-specific errors/warnings
- [ ] **Add code snippet/template library management UI**
  - [ ] Allow users to create, edit, and manage their own snippets/templates
- [x] Documentation and accessibility for snippet/template insertion and multi-language support are complete.
- [x] Advanced Python IntelliSense (LSP) is available as an option in all code/script editing areas. Requires a running Python language server at ws://localhost:3001.
- [x] Custom formatters for Python (Ruff WASM) and JS/TS (Prettier) are available via the customFormatter prop and formatCode utility.

### D. Validation
- [ ] **Improve UI for displaying workflow validation results**
  - [ ] Show errors/warnings directly on the canvas and/or nodes
  - [ ] Add summary/status indicator for workflow validity

### E. Documentation & Checklist
- [ ] Keep this checklist up to date as work progresses
- [ ] Remove/merge duplicate items from `PHASE_2_CORE_FUNCTIONALITY_CHECKLIST.md` and reference this doc for frontend tracking

---

## References
- Backend work for these sections is complete (see `PHASE_2_CORE_FUNCTIONALITY_CHECKLIST.md`).
- This checklist supersedes previous frontend checklists for Phase 2.
- Multi-language snippet support is implemented in all code/script editing areas via CodeEditor and PropertiesPanel. 