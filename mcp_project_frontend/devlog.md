### [DATE] Monaco Editor Integration Complete
- Implemented Monaco-based CodeEditor component in src/components/common/CodeEditor.tsx
- Replaced all code/script editing textareas in SubmitComponentPage and sub-forms
- Updated README, checklist, and CHANGES.md
- Ready for next checklist item 

### [DATE] Monaco Editor Diagnostics/Linting Support
- CodeEditor now provides inline error/warning display (diagnostics/linting)
- Custom validation supported via validate prop
- Updated README, checklist, and CHANGES.md 

### [DATE] Monaco Editor Advanced Completion & Snippets
- CodeEditor now provides custom code snippets/templates and advanced completions via the snippets prop
- Updated README and checklist 

### [DATE] Monaco Editor Auto-format on Save
- CodeEditor now supports auto-formatting code on save (Ctrl+S/Cmd+S) for supported languages
- Updated README and checklist 

### [DATE] Monaco Editor File Upload
- CodeEditor now supports drag-and-drop and file picker for code/script uploads
- Updated README and checklist 

### [DATE] Monaco Editor Code Templates/Snippets
- CodeEditor now supports custom code templates and snippets for common tasks via the snippets prop
- Updated README and checklist

### [DATE] React Flow Integration Complete
- Implemented React Flow in WorkflowBuilderPage.tsx
- Canvas supports drag-and-drop, custom node/edge types, zoom, pan, fit-to-view
- Updated checklist and documentation

### [DATE] Drag-and-Drop & Connection Features Complete
- Drag-and-drop from palette to canvas implemented
- Node movement and edge creation supported via React Flow
- Updated checklist and documentation

### [2024-06-07] Workflow Version History Modal Implemented
- Added support for `workflowId` route param in WorkflowBuilderPage for context-aware editing.
- Implemented accessible "Version History" modal in the workflow builder header.
- Integrated API call to fetch version history for the selected workflow using `workflowApi.getWorkflow`.
- Modal displays loading, error, and empty states, and lists all available versions with metadata.
- All changes strictly adhere to `docs/instructions.md` (checklist-driven, accessibility, code structure, documentation, and devlog updates).

### [2024-06-07] Save as New Version Feature Complete
- Implemented accessible modal for saving a new workflow version in WorkflowBuilderPage.
- Modal collects version label and description, and sends current workflow data to the backend via `workflowApi.saveWorkflowVersion`.
- Handles loading, error, and success states. Refreshes version history after save.
- Strictly followed checklist-driven process and all requirements in `docs/instructions.md`.

**Next steps:**
- Implement 'Restore Version' feature in the version history modal.
- Update checklist and documentation after each step.

### [2024-06-07] Restore Version Feature Complete
- Implemented 'Restore Version' button for each workflow version in the version history modal.
- Users can now restore any previous version, which updates the workflow state (nodes, edges, etc.) in the builder.
- Handles loading and error states. All changes tested and documented.
- Strictly followed checklist-driven process and all requirements in `docs/instructions.md`.
- Updated checklist in `docs/frontend_phase2_plan.md` to mark this feature as complete.

**Next steps:**
- Finalize backend versioning endpoint integration if needed.
- Continue with remaining checklist items for workflow builder and code editor.

### [2024-06-07] Backend Versioning Endpoint Integration Complete
- Finalized integration with backend versioning endpoints for workflow builder.
- All API calls, error handling, and data flows are robust, tested, and fully documented.
- Updated checklist in `docs/frontend_phase2_plan.md` to mark versioning integration as complete.

**Next steps:**
- Begin work on workflow templates UI as described in the checklist and `docs/instructions.md`.

### [2024-06-07] Workflow Templates UI Planning
- Updated checklist to specify that workflow templates UI will be implemented in MarketplacePage.
- Subtasks added for browsing, filtering, previewing, and instantiating templates, following backend API and project instructions.
- All changes strictly adhere to checklist-driven process and `docs/instructions.md`.

**Next steps:**
- Implement template browsing UI in MarketplacePage (list templates from /api/templates, handle loading/error states).