
# AI Ops Console

## 1. Overview

The AI Ops Console is a frontend application designed to provide a comprehensive interface for managing AI operations. It aims to offer a modular, intuitive, and data-driven platform for users to discover AI components, build complex workflows, monitor their execution, and submit new components with the help of an AI-powered coding assistant.

The application is built as a single-page application (SPA) using React and TypeScript, leveraging modern JavaScript features and direct browser ESM module imports for dependencies.

## 2. Features

*   **Dashboard**: Personalized overview with recommended components, trending workflows, and system health.
*   **Component Marketplace**:
    *   Browse and discover AI components (preset and user-submitted).
    *   Faceted search and filtering (by type, compliance, cost).
    *   Detailed view for each component.
*   **Workflow Builder (Conceptual)**:
    *   Visual canvas placeholder for constructing workflows (React Flow integration planned).
    *   Component palette to drag-and-drop components.
    *   Properties panel for configuring selected nodes/workflow.
*   **Execution Monitor**:
    *   Track historical workflow runs.
    *   Filter runs by status.
    *   Detailed view for each run.
*   **Submit New Component**:
    *   Dynamic form tailored to various component types (Python Script, TypeScript Script, Jupyter Notebook, LLM Prompt Agent, Streamlit App, MCP, etc.).
    *   Input common metadata (name, description, version, tags, schemas, visibility).
    *   **AI Coding Assistant**: Integrated chat bot (powered by Gemini API) to help users write code or configure components based on the selected type and current form data.
*   **Responsive Design**: UI adapts to different screen sizes (desktop-focused for complex views).
*   **Mock Authentication**: Simple user login/logout persistence using `localStorage`.
*   **Custom Component Persistence**: User-submitted components are saved to `localStorage`.

## 3. Tech Stack

*   **Frontend Framework**: React 19 (using `esm.sh` for imports)
*   **Language**: TypeScript
*   **Routing**: React Router DOM (v6, via `esm.sh`)
*   **Styling**:
    *   Tailwind CSS (CDN version with JIT configuration)
    *   Global CSS in `index.html` (Inter font, scrollbar styling, CSS color variables)
*   **AI Assistant**: Google Gemini API (`@google/genai` via `esm.sh`)
*   **Icons**: Heroicons (as inline SVG components)
*   **State Management**: React Context API (for Auth and Components)
*   **Module System**: ES Modules (ESM) via `importmap` in `index.html`

## 4. Project Structure

The project is structured to separate concerns, making it easier to navigate and maintain.

```
.
├── README.md                   # This file
├── index.html                  # Main HTML entry point, loads scripts and styles
├── index.tsx                   # Main React application bootstrap
├── metadata.json               # Application metadata (e.g., permissions for a host environment)
├── App.tsx                     # Root application component with routing logic
├── types.ts                    # TypeScript type definitions and interfaces
├── icons.tsx                   # SVG icon components
├── constants.tsx               # Global constants (nav items, dummy data, enums, etc.)
├── contexts/                   # React Context API providers and hooks
│   ├── AuthContext.tsx         # Authentication state management
│   └── ComponentContext.tsx    # AI Component data management (preset & custom)
├── hooks/                      # Custom React hooks
│   └── useAuth.ts              # Hook to access AuthContext
├── components/                 # Reusable UI components
│   ├── common/                 # Generic components (Button, Card, Modal)
│   ├── layout/                 # Layout structure (Sidebar, Topbar)
│   ├── marketplace/            # Components specific to the Marketplace page
│   ├── workflow_builder/       # Components specific to the Workflow Builder page
│   ├── execution_monitor/      # Components specific to the Execution Monitor page
│   └── submit_component/       # Components specific to the Submit Component page (e.g., ChatAssistant)
└── pages/                      # Top-level page components
    ├── DashboardPage.tsx
    ├── MarketplacePage.tsx
    ├── WorkflowBuilderPage.tsx
    ├── ExecutionMonitorPage.tsx
    └── SubmitComponentPage.tsx
```

## 5. File Breakdown

This section provides a detailed explanation of each file and its role in the application.

---

### `index.html`

*   **Purpose**: The main HTML file that serves as the entry point for the web application.
*   **Key Contents**:
    *   Standard HTML structure (`<head>`, `<body>`).
    *   `<meta>` tags for viewport and character set.
    *   `<title>` of the application.
    *   **Tailwind CSS**: Loads Tailwind CSS via CDN and includes an inline configuration script for theme extensions (colors).
    *   **Global Styles**: Inline `<style>` block for:
        *   Setting the `Inter` font family.
        *   Defining CSS custom properties (variables) for the color palette, which are then used by Tailwind's theme.
        *   Custom scrollbar styling for WebKit browsers.
    *   **Google Fonts**: Links to import the `Inter` font.
    *   **Import Map**: Defines aliases for ESM module imports (React, React DOM, React Router, `@google/genai`) from `esm.sh`. This allows using bare module specifiers in `.tsx` files.
    *   Root `<div>` (`<div id="root"></div>`): The DOM element where the React application will be mounted.
    *   Main Script Load: `<script type="module" src="/index.tsx"></script>` which loads and executes the main React application logic.

---

### `index.tsx`

*   **Purpose**: The main TypeScript file that bootstraps the React application.
*   **Key Contents**:
    *   Imports React, ReactDOM, the main `App` component, `AuthProvider`, and `ComponentProvider`.
    *   Gets the root DOM element (`document.getElementById('root')`).
    *   Uses `ReactDOM.createRoot()` (React 18+ API) to create a new root for rendering.
    *   Renders the `App` component wrapped within `React.StrictMode`, `AuthProvider`, and `ComponentProvider`. `StrictMode` helps with identifying potential problems in an application. `AuthProvider` provides authentication context, and `ComponentProvider` provides AI component data context.

---

### `metadata.json`

*   **Purpose**: Contains metadata about the application. This is often used in environments that host web applications and need to know details like name, description, or required permissions.
*   **Key Contents**:
    *   `name`: The display name of the application ("AI Ops Console").
    *   `description`: A brief description of the application.
    *   `requestFramePermissions`: An array that would list permissions the app needs if it were running in an iframe or a specific hosting environment (e.g., "camera", "microphone"). Currently empty.

---

### `App.tsx`

*   **Purpose**: The main application component that sets up the overall layout and routing logic.
*   **Key Contents**:
    *   Imports necessary components from `react-router-dom`, layout components (`Sidebar`, `Topbar`), page components, and the `useAuth` hook.
    *   **`LoginPage` (Mock)**: A simple functional component for demonstrating a login screen. It uses the `useAuth` hook to simulate a login.
    *   **`AuthenticatedApp`**: A functional component that renders the main application layout (Sidebar, Topbar, and content area with page routes) when a user is authenticated.
    *   **Main `App` Component**:
        *   Uses the `useAuth` hook to get the current user state.
        *   Uses `HashRouter` for client-side routing (suitable for SPAs without complex server-side routing configuration, especially in static hosting environments).
        *   Defines `Routes`:
            *   If no user is authenticated, it shows the `/login` route or redirects any other path to `/login`.
            *   If a user is authenticated, it renders the `AuthenticatedApp` component for all paths.
    *   **Route Definitions within `AuthenticatedApp`**:
        *   Defines routes for `/dashboard`, `/marketplace` (and `/marketplace/component/:componentId` for detail view), `/builder` (and `/builder/:workflowId`), `/monitor` (and `/monitor/run/:runId`), and the `/submit-component` page.
        *   Includes a default route (`/`) and a fallback route (`*`) that navigate to `/dashboard`.

---

### `types.ts`

*   **Purpose**: Defines shared TypeScript types and interfaces used throughout the application to ensure type safety and consistency.
*   **Key Contents**:
    *   `NavItem`: Interface for navigation items (path, name, icon).
    *   `NotebookCell`: Interface for cells in a Jupyter Notebook representation (id, type: 'code' | 'markdown', content).
    *   `SpecificComponentType`: A union type for all specific AI component types (e.g., 'Python Script', 'LLM Prompt Agent').
    *   `AIComponent`: A core interface representing an AI component with fields like `id`, `name`, `type` (using `SpecificComponentType`), `description`, `version`, `tags`, `icon`, `inputSchema`, `outputSchema`, `compliance`, `costTier`, `visibility`, `isCustom` (flag for user-submitted components), and `typeSpecificData` (an object to hold configuration unique to each `SpecificComponentType`).
    *   `AIComponentCostTier`: Union type for cost tiers ('Free', 'Low', 'Medium', 'High').
    *   `Workflow`: Interface for workflow definitions.
    *   `WorkflowRunStatus`: Enum for the status of workflow runs.
    *   `WorkflowRun`: Interface for workflow execution instances.
    *   `SystemStatus`: Interface for representing the health of system services.
    *   `User`: Interface for user data (id, name, email, avatarUrl, role).
    *   `ChatMessage`: Interface for messages in the AI chat assistant (id, text, sender, timestamp).

---

### `icons.tsx`

*   **Purpose**: Contains a collection of SVG icons used throughout the application, defined as React functional components. This approach allows for easy customization of icon props (like `className`).
*   **Key Contents**:
    *   Each icon (e.g., `DashboardIcon`, `SearchIcon`, `PythonIcon`, `ChatBubbleLeftRightIcon`) is a React functional component (`React.FC<React.SVGProps<SVGSVGElement>>`).
    *   The SVG markup is directly embedded in the JSX.
    *   Props (`{...props}`) are spread onto the `<svg>` element, allowing `className`, `width`, `height`, etc., to be passed.
    *   Includes general navigation icons, action icons, status icons, and specific icons for different component types. Some specific icons (like `PythonIcon`) reuse more generic ones (like `CodeBracketIcon`).

---

### `constants.tsx`

*   **Purpose**: Defines global constants, dummy data for UI population, utility functions, and static configurations used across the application.
*   **Key Contents**:
    *   `NAV_ITEMS`: An array of `NavItem` objects for sidebar navigation.
    *   `COMPONENT_TYPE_ICON_MAP`: A record mapping `SpecificComponentType` strings to their corresponding icon components from `icons.tsx`.
    *   `DUMMY_COMPONENTS_PRESET`: An array of preset `AIComponent` objects, serving as initial data for the marketplace. These include example `typeSpecificData`.
    *   `DUMMY_WORKFLOWS` and `DUMMY_WORKFLOW_RUNS`: Arrays of dummy data for workflows and their execution history.
    *   `DUMMY_SYSTEM_STATUS`: Array of dummy data for system health indicators.
    *   `SUBMITTABLE_COMPONENT_TYPES`: An array of `SpecificComponentType` strings that can be selected when submitting a new component.
    *   `ALL_COMPONENT_TYPES`: Combines `SUBMITTABLE_COMPONENT_TYPES` (used for filters).
    *   `COMPONENT_COMPLIANCE_OPTIONS`, `COMPONENT_COST_TIERS`, `COMPONENT_VISIBILITY_OPTIONS`, `LLM_MODELS`: Arrays for dropdowns and selection options in forms.
    *   `AI_OPS_CONSOLE_LOGO`: A JSX element for the application logo displayed in the sidebar.
    *   `LOCAL_STORAGE_CUSTOM_COMPONENTS_KEY`: String key for `localStorage`.
    *   `DEFAULT_COMPONENT_ICON`: A default fallback icon.
    *   `getIconForComponentType`: A utility function that returns the appropriate React icon element for a given `SpecificComponentType`, using `COMPONENT_TYPE_ICON_MAP`.

---

### `contexts/AuthContext.tsx`

*   **Purpose**: Provides authentication state and logic (login, logout) to the entire application using React's Context API.
*   **Key Contents**:
    *   `AuthContextType`: Interface defining the shape of the context value (user, setUser, login, logout).
    *   `AuthContext`: Created using `createContext`.
    *   `AuthProvider`: The provider component that wraps parts of the application (or the whole app).
        *   Manages the `user` state using `useState`.
        *   Initializes the `user` state by attempting to load it from `localStorage`. If not found or parsing fails, it defaults to a mock "Admin" user.
        *   `login` function: Sets the user state and saves it to `localStorage`.
        *   `logout` function: Clears the user state and removes it from `localStorage`.
        *   Provides the `user`, `setUser`, `login`, and `logout` functions to consuming components via the context.

---

### `contexts/ComponentContext.tsx`

*   **Purpose**: Manages the state of AI components, including both preset (dummy) components and custom (user-submitted) components. Custom components are persisted using `localStorage`.
*   **Key Contents**:
    *   `ComponentContextType`: Interface defining the context value (`allComponents`, `addCustomComponent`, `getComponentById`).
    *   `ComponentContext`: Created using `createContext`.
    *   `ComponentProvider`: The provider component.
        *   Manages `customComponents` state.
        *   `useEffect`: Loads custom components from `localStorage` on initial mount. It reconstructs the `icon` prop (as ReactNodes are not serializable) using `getIconForComponentType`.
        *   `saveCustomComponents`: A `useCallback` function to save the current list of custom components to `localStorage` (stripping non-serializable `icon` props before saving).
        *   `addCustomComponent`: A `useCallback` function to add a new custom component. It generates a unique ID, assigns an icon, flags it as `isCustom`, updates the state, and calls `saveCustomComponents`.
        *   `allComponents`: A `useMemo` hook that combines the `DUMMY_COMPONENTS_PRESET` with the `customComponents` from state. It ensures default values and icons are applied correctly.
        *   `getComponentById`: A `useCallback` function to find and return a component by its ID from the `allComponents` list.
        *   Provides `allComponents`, `addCustomComponent`, and `getComponentById` to consuming components.
    *   `useComponents`: Custom hook to easily access the `ComponentContext`.

---

### `hooks/useAuth.ts`

*   **Purpose**: A custom React hook to simplify accessing the `AuthContext`.
*   **Key Contents**:
    *   Uses `useContext(AuthContext)` to get the authentication context.
    *   Throws an error if the hook is used outside of an `AuthProvider`, ensuring proper context setup.
    *   Returns the context value (`user`, `setUser`, `login`, `logout`).

---

### `components/common/`

This directory contains generic, reusable UI components.

*   **`Card.tsx`**:
    *   A versatile card component for displaying content in a structured way.
    *   Props: `children`, `className`, `title`, `titleClassName`, `actions` (for buttons/icons in the header), `onClick`, `noPadding`.
    *   Provides consistent styling for cards (background, shadow, rounded corners).
*   **`Button.tsx`**:
    *   A customizable button component.
    *   Props: `children`, `variant` ('primary', 'secondary', 'danger', 'ghost', 'outline'), `size` ('sm', 'md', 'lg'), `leftIcon`, `rightIcon`, `isLoading`, standard button attributes.
    *   Handles different visual styles, sizes, loading states (with spinner), and icon placement.
*   **`Modal.tsx`**:
    *   A generic modal/dialog component.
    *   Props: `isOpen`, `onClose`, `title`, `children`, `size` ('sm' to 'full'), `footer`.
    *   Manages modal visibility, provides a backdrop, and includes sections for title, content, and an optional footer. Allows closing by clicking the backdrop or a close button.

---

### `components/layout/`

Components responsible for the main application layout.

*   **`Sidebar.tsx`**:
    *   The main navigation sidebar on the left.
    *   Displays the application logo (`AI_OPS_CONSOLE_LOGO`) and a list of navigation links (`NAV_ITEMS`).
    *   Uses `NavLink` from `react-router-dom` to highlight the active link.
    *   Icons in nav links dynamically change color based on active state.
    *   Fixed position, with consistent styling.
*   **`Topbar.tsx`**:
    *   The header bar at the top of the content area.
    *   Includes:
        *   A global search input field.
        *   A notification bell icon (placeholder).
        *   User profile display (avatar, name) with a dropdown menu for "Your Profile", "Settings", and "Sign out".
        *   Uses `useAuth` to get user information and the `logout` function.
    *   Sticky position, with consistent styling.

---

### `components/marketplace/`

Components used specifically within the Component Marketplace page.

*   **`ComponentCard.tsx`**:
    *   Displays a summary of an AI component in a card format within the marketplace grid.
    *   Shows component icon, name, version, type, description (truncated), tags, and a "View Details" button.
    *   The `onSelect` prop is called when "View Details" is clicked, typically to open the `ComponentDetailView`.
*   **`FilterPanel.tsx`**:
    *   A panel (usually on the side) that allows users to filter the list of components in the marketplace.
    *   Uses `CheckboxFilter` sub-components for different filter groups (Component Type, Compliance, Cost Tier).
    *   Takes `filters` (current filter state) and `onFilterChange` (callback to update filters) as props.
*   **`ComponentDetailView.tsx`**:
    *   A modal component that displays detailed information about a selected AI component.
    *   Shows component name, icon, version, type, description, tags, compliance details, cost tier, input/output schemas (as formatted JSON), and placeholders for sandbox/dependency visualization.
    *   Includes "Close" and "Add to Workflow" buttons.
    *   Managed by `isOpen` and `onClose` props.

---

### `components/workflow_builder/`

Components used on the Workflow Builder page. These are mostly placeholders as the actual workflow canvas (e.g., using React Flow) is not fully implemented.

*   **`ComponentPalette.tsx`**:
    *   A sidebar panel within the Workflow Builder that lists available AI components.
    *   Users would drag components from this palette onto the workflow canvas.
    *   Uses `useComponents` to get `allComponents` (public and user's custom components).
    *   Includes a search bar to filter components within the palette.
    *   Groups components by type (with "My Custom Components" appearing first).
    *   Each item (`PaletteItem`) is draggable and sets `dataTransfer` data for React Flow (conceptual).
*   **`PropertiesPanel.tsx`**:
    *   A sidebar panel to display and edit properties of the selected node on the workflow canvas or global workflow settings.
    *   Currently, it's a placeholder showing example input fields. In a real implementation, it would dynamically render configuration options based on the selected component's schema or workflow properties.

---

### `components/execution_monitor/`

Components for the Execution Monitor page.

*   **`RunsTable.tsx`**:
    *   Displays a table of workflow execution runs.
    *   Columns: Run ID, Workflow Name, Status (with a `StatusBadge`), Start Time, Duration, Cost, Initiator, and an Actions column (e.g., "Details" button).
    *   The `StatusBadge` sub-component provides a visually distinct badge for each run status.
    *   `onSelectRun` prop is called when a run's "Details" button is clicked.
*   **`RunDetailView.tsx`**:
    *   A modal component to show detailed information about a specific workflow run.
    *   Displays all fields of a `WorkflowRun` object.
    *   Includes placeholders for logs and metrics.
    *   Offers contextual actions like "Abort Run" (if running) or "Rerun Workflow".

---

### `components/submit_component/ChatAssistant.tsx`

*   **Purpose**: An AI-powered chat assistant to help users create and configure components on the "Submit Component" page.
*   **Key Contents**:
    *   Uses `GoogleGenAI` from `@google/genai` to interact with the Gemini API.
    *   **API Key Handling**: Retrieves `API_KEY` from `process.env.API_KEY`. Displays an error if the key is not configured in the environment. **Crucially, it does not provide a UI for users to enter the API key.**
    *   **Chat Initialization**:
        *   Creates a chat session using `ai.current.chats.create()`.
        *   Model: `gemini-2.5-flash-preview-04-17`.
        *   Sets a dynamic `systemInstruction` for the Gemini model based on the `selectedComponentType` to provide context-aware assistance.
        *   Uses `thinkingConfig: { thinkingBudget: 0 }` for lower latency responses.
    *   **State Management**: `isOpen` (for chat panel visibility), `messages` (array of `ChatMessage`), `userInput`, `isLoading`, `error`.
    *   **Message Sending**:
        *   `handleSendMessage` function:
            *   Appends user message to the `messages` state.
            *   Constructs a prompt for Gemini that includes the user's input *and* relevant context from the current component form data (`currentComponentData`).
            *   Uses `chatInstance.current.sendMessageStream()` to get streaming responses from Gemini.
            *   Updates the bot's message in the UI incrementally as chunks arrive from the stream.
    *   **UI**:
        *   A collapsible/expandable chat panel fixed to the bottom-right of the screen.
        *   Displays chat messages from user and bot, with distinct styling.
        *   Input field for user to type messages.
        *   Send button.
        *   Handles loading indicators and error messages.
    *   **Contextual Assistance**: The assistant's effectiveness is enhanced by providing it with the current state of the component form.

---

### `pages/DashboardPage.tsx`

*   **Purpose**: The main landing page after login, providing an overview and quick access.
*   **Key Contents**:
    *   Displays a welcome header.
    *   **Quick Actions Card**: Buttons for "New Workflow", "Starred Items", "Recent Runs".
    *   **Personalized Feed**:
        *   Uses `PersonalizedFeedCard` sub-component to display "Recommended Components" and "Trending Workflows" (using dummy data).
        *   Links items to their respective detail/builder pages.
    *   **System Health Monitor**:
        *   Uses `SystemHealthItem` sub-component to display the status of various system services (dummy data).
        *   Icons and colors indicate status (OK, Warning, Error).
    *   **Recent Activity Card**: Placeholder list of recent activities.

---

### `pages/MarketplacePage.tsx`

*   **Purpose**: Allows users to browse, search, and filter AI components.
*   **Key Contents**:
    *   Page header and description.
    *   **Search Bar**: Input field to search components by name, description, or tags.
    *   **Layout**: Two-column layout with `FilterPanel` on the left and the component grid on the right.
    *   **`FilterPanel`**: Allows filtering by component type, compliance, and cost tier.
    *   **Component Grid**: Displays `ComponentCard` components for each filtered AI component.
    *   **Data Source**: Uses `useComponents()` hook from `ComponentContext` to get `allComponents` (presets + custom).
    *   **Filtering Logic**: `useMemo` hook recalculates `filteredComponents` based on `searchTerm` and `filters`. It also ensures that only 'Public' components or the user's own `isCustom` components are shown.
    *   **Detail View**:
        *   Uses `ComponentDetailView` modal to show details when a component is selected.
        *   Integrates with `react-router-dom`'s `useParams` and `useNavigate` to show/hide the modal based on the `/marketplace/component/:componentId` route.

---

### `pages/WorkflowBuilderPage.tsx`

*   **Purpose**: The page for visually constructing and configuring AI workflows.
*   **Key Contents**:
    *   **Note**: This page is largely a placeholder for a full React Flow (or similar library) integration.
    *   Page header with action buttons (Save, Validate, Run Test - currently non-functional).
    *   **Layout**: Three-column layout:
        *   Left: `ComponentPalette` for dragging components.
        *   Center: Placeholder for the visual workflow canvas. Displays an icon and text indicating where React Flow would be integrated. The commented-out code shows the basic structure for React Flow (nodes, edges, drag & drop handlers).
        *   Right: `PropertiesPanel` for configuring selected nodes/workflow.
    *   The drag-and-drop logic (commented out) demonstrates how component data would be transferred from the palette to the canvas to create new nodes.

---

### `pages/ExecutionMonitorPage.tsx`

*   **Purpose**: Allows users to track live and historical workflow runs.
*   **Key Contents**:
    *   Page header.
    *   **Status Filter**: A `select` dropdown to filter runs by status (Pending, Running, Success, Failed, Aborted, All).
    *   **`RunsTable`**: Displays the filtered list of workflow runs (using dummy data).
    *   **`RunDetailView`**: A modal to show details of a selected run.
    *   **Routing Integration**: Similar to `MarketplacePage`, it uses `useParams` and `useNavigate` to manage the display of the `RunDetailView` modal based on the `/monitor/run/:runId` route.

---

### `pages/SubmitComponentPage.tsx`

*   **Purpose**: Allows users to submit new AI components to the system. Features a dynamic form based on the selected component type and integrates the `ChatAssistant`.
*   **Key Contents**:
    *   Page header.
    *   **Form Structure**:
        *   **Type Selection**: A dropdown to select the `SpecificComponentType`.
        *   **Common Fields**: Inputs for name, version, description, tags, input/output schemas (JSON textareas), compliance (checkboxes), cost tier, and visibility (radio buttons).
        *   **Dynamic Type-Specific Form**:
            *   The `renderTypeSpecificForm` function conditionally renders different sub-form components based on `selectedType`.
            *   **Sub-Form Components** (defined within the file):
                *   `CodeEditorForm`: Textarea for Python/TypeScript code.
                *   `NotebookEditorForm`: Interface to add/manage/edit markdown and code cells for Jupyter Notebooks.
                *   `LLMAgentEditorForm`: Fields for LLM model, system prompt, user prompt template, temperature, max tokens.
                *   `StreamlitAppEditorForm`: Fields for Git repo URL, main script path, and requirements content.
                *   `MCPEditorForm`: Textarea for MCP configuration (JSON/YAML).
                *   Generic types ('Data', 'Utility', 'Output') show a message if no specific fields are defined.
    *   **State Management**:
        *   `selectedType`: Stores the chosen component type.
        *   `commonFormData`: State for fields common to all component types.
        *   `typeSpecificData`: State for data unique to the selected component type.
        *   `errors`: State for form validation errors.
        *   `submissionStatus`: Tracks the status of the form submission ('idle', 'success', 'error').
    *   **Form Handling**:
        *   `handleCommonChange`, `handleCheckboxChange`, `handleTypeSpecificChange`: Functions to update form state.
        *   `validateForm`: Performs client-side validation for required fields and correct formats (e.g., semver for version, valid JSON for schemas). Includes type-specific validation rules.
        *   `handleSubmit`:
            *   Calls `validateForm`.
            *   If valid, constructs an `AIComponent` object from `commonFormData` and `typeSpecificData`.
            *   Calls `addCustomComponent` from `ComponentContext` to save the new component (which persists to `localStorage`).
            *   Updates `submissionStatus` and navigates to the marketplace on success.
    *   **AI Chat Assistant**:
        *   Renders the `<ChatAssistant />` component.
        *   Passes `selectedComponentType` and `currentFullComponentData` (a snapshot of the current form state) to the assistant for contextual help.
    *   `FormRow`: A helper sub-component for consistent layout of labels, inputs, and error messages.

## 6. Key Functionality Details

### Component Management

*   **Preset Components**: Defined in `constants.tsx` (`DUMMY_COMPONENTS_PRESET`). These are always available.
*   **Custom Components**: Users can submit new components via the `SubmitComponentPage`.
    *   These components are managed by `ComponentContext`.
    *   They are stored in the browser's `localStorage` under the key `aiOpsCustomComponents` (defined in `constants.tsx`).
    *   The `ComponentContext` handles loading from and saving to `localStorage`, ensuring that ReactNode `icon` props are reconstructed on load as they are not serializable.
    *   Custom components are flagged with `isCustom: true`.
*   **Display**: The `MarketplacePage` and `ComponentPalette` (in Workflow Builder) display a combination of preset and custom components, filtering by visibility (public presets and all custom components for the current user).

### AI Coding Assistant (Gemini API Integration)

*   **Location**: Integrated into the `SubmitComponentPage.tsx` via the `ChatAssistant.tsx` component.
*   **API**: Uses the `@google/genai` SDK to interact with the Google Gemini API.
    *   Model: `gemini-2.5-flash-preview-04-17`.
*   **API Key Requirement**:
    *   The API key **MUST** be provided as an environment variable `process.env.API_KEY`.
    *   The application code (`ChatAssistant.tsx`) reads this variable directly: `const API_KEY = process.env.API_KEY;`.
    *   **There is NO UI for users to enter or manage the API key.** The application assumes this key is pre-configured in the execution environment.
    *   If the key is not found, the AI Assistant will display an error message and be non-functional.
*   **Contextual Help**:
    *   The assistant's system prompt is dynamically set based on the `selectedComponentType` on the submission form.
    *   When the user sends a message, the current data from the component submission form (`currentComponentData`) is appended to the user's prompt. This provides Gemini with context about what the user is trying to build, allowing for more relevant assistance.
*   **Streaming Responses**: Uses `chat.sendMessageStream()` for interactive, real-time responses from the AI, updating the chat UI incrementally.
*   **Low Latency**: Configured with `thinkingConfig: { thinkingBudget: 0 }` to potentially reduce latency for chat-like interactions.
*   **Conversation History**: `ai.chats.create()` is used, which inherently manages conversation history for the session, allowing follow-up questions.

### Authentication (Mock)

*   A simple mock authentication system is implemented using `AuthContext`.
*   When a user "logs in" (via a mock login button on a conceptual `LoginPage`), their user data is stored in `localStorage`.
*   `AuthProvider` loads this user data on application start.
*   `useAuth` hook provides access to user data and login/logout functions.
*   This is for demonstration purposes and would need to be replaced with a real authentication backend in a production system.

### State Management

*   **React Context API**: Used for global state management.
    *   `AuthContext`: Manages user authentication state.
    *   `ComponentContext`: Manages the list of AI components (both preset and custom).

### Routing

*   **React Router DOM v6**: Handles client-side navigation.
*   **`HashRouter`**: Used for routing, which is convenient for single-page applications hosted statically as it uses the URL hash (`#`) to manage routes without requiring server-side configuration.
*   Routes are defined in `App.tsx` for all major pages and detail views (e.g., specific component or run).

## 7. Getting Started / Running the App

This application is designed to run directly in a modern browser that supports ES Modules and `importmap`.

### Prerequisites

*   A modern web browser (e.g., Chrome, Firefox, Edge, Safari) with JavaScript enabled.
*   For the **AI Coding Assistant** feature to work:
    *   You **MUST** have a valid Google Gemini API key.
    *   This API key needs to be accessible as an environment variable named `API_KEY` in the context where the application's JavaScript is executed.
        *   **Important**: Since this is a frontend-only project structure running directly via `index.html` without a typical Node.js backend or build process that injects environment variables, setting `process.env.API_KEY` is tricky.
        *   **Option 1 (Development - Insecure for Browser):** You could temporarily hardcode it in `ChatAssistant.tsx` for local testing: `const API_KEY = "YOUR_ACTUAL_API_KEY";`. **NEVER commit this to version control.**
        *   **Option 2 (Using a Local Server with Env Injection):** If you serve `index.html` via a simple local server (like `live-server` or a custom Node.js server), that server might have mechanisms to inject environment variables or serve a dynamically generated script that sets `window.process = { env: { API_KEY: "..." } }` before `index.tsx` runs. This is beyond the current project's scope.
        *   **Option 3 (Build Step - Ideal):** In a typical React project with a build step (like Vite or Create React App), you would use `.env` files (e.g., `.env.local`) and the build tool would handle making `VITE_API_KEY` or `REACT_APP_API_KEY` available as `process.env.VITE_API_KEY`. You would then adapt the code to use `process.env.VITE_API_KEY`.
        *   **For the current structure, the code expects `process.env.API_KEY`. Without a build step or server-side injection, this global `process` object might not exist or might not have `env.API_KEY` defined, leading to the AI Assistant being disabled.**

### Running the Application

1.  Ensure all project files are in a directory.
2.  Open the `index.html` file directly in your web browser.
    *   Alternatively, serve the project directory using a simple HTTP server (e.g., `npx serve .` or Python's `http.server`). This can help avoid potential issues with file path resolutions or CORS if you were to fetch local JSON files (though not currently done).
3.  The application should load, and you can navigate through the different pages.

### AI Assistant API Key

As mentioned above, for the AI Coding Assistant in the "Submit Component" page to function, the `process.env.API_KEY` must be correctly set up and accessible to the JavaScript runtime. If not, the assistant will show an error and be disabled. **The application strictly adheres to the guideline of not providing a UI to input this key.**

## 8. Styling

*   **Tailwind CSS**: Utilized via a CDN link in `index.html`.
    *   An inline `tailwind.config` script in `index.html` extends the default theme, primarily for custom color definitions that use CSS variables.
*   **CSS Custom Properties (Variables)**: Defined in a `<style>` block in `index.html` for the base color palette (e.g., `--color-primary`, `--color-neutral-dark`). These are then referenced by Tailwind's configuration.
*   **Global Styles**:
    *   The `Inter` font family is applied to the `body`.
    *   Custom scrollbar styling for a more modern look in WebKit-based browsers.
*   **Component-Level Styling**: Tailwind utility classes are used extensively within `.tsx` components for styling.

## 9. Known Limitations & Future Considerations

*   **No Backend**: This is a frontend-only application. All "backend" operations (like saving components, user authentication) are mocked using `localStorage` or dummy data. A real backend would be needed for persistent storage, user management, and actual workflow execution.
*   **Workflow Builder Canvas**: The Workflow Builder page currently has a placeholder for the visual canvas. Integration with a library like React Flow is planned for full drag-and-drop functionality.
*   **API Key for AI Assistant**: The method for providing `process.env.API_KEY` in a purely static frontend setup (without a build step) is a common challenge. The current code relies on it being available in the global `process.env` object.
*   **Code Editor in Submit Form**: The "Python Script" and "TypeScript Script" submission forms use basic `<textarea>` elements. For a better user experience, integrating a proper code editor component (e.g., Monaco Editor) would be beneficial.
*   **Jupyter Notebook Form**: The notebook cell editor is a simplified representation. A more feature-rich editor or direct `.ipynb` file parsing could be implemented.
*   **Error Handling**: While some basic error handling is present (e.g., for AI Assistant API calls, form validation), it could be made more robust and user-friendly across the application.
*   **Testing**: No automated tests (unit, integration, e2e) are included in this project structure.
*   **Accessibility (a11y)**: While standard HTML elements and Tailwind aim for some level of accessibility, a dedicated a11y review and improvements (e.g., more ARIA attributes for custom interactive elements) would be necessary for production.
*   **Performance Optimization**: For larger datasets or more complex UIs, performance optimizations (e.g., memoization, code splitting if a bundler were used) might be needed.
*   **Real-time Updates**: Features like the Execution Monitor would benefit from real-time updates via WebSockets in a production scenario.
*   **Security**: As a frontend-only app with mock auth, security considerations for a real application (input sanitization, XSS prevention, secure API communication, proper authentication/authorization) are not addressed.
```