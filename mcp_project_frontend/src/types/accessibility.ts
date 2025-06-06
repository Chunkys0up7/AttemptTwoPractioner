/**
 * Accessibility types for the workflow system
 */

export interface AccessibilityState {
  isKeyboardNavigation: boolean;
  isScreenReaderActive: boolean;
  currentFocus: string | null;
  previousFocus: string | null;
  keyboardMode: KeyboardMode;
  selectedNode: string | null;
  selectedEdge: string | null;
  activePanel: PanelType | null;
}

export enum KeyboardMode {
  NAVIGATION = 'NAVIGATION',
  SELECTION = 'SELECTION',
  EDIT = 'EDIT',
}

export enum PanelType {
  NODE_PALETTE = 'NODE_PALETTE',
  PROPERTIES = 'PROPERTIES',
  EXECUTION = 'EXECUTION',
  MONITORING = 'MONITORING',
}

export interface AriaAttributes {
  role?: string;
  'aria-label'?: string;
  'aria-labelledby'?: string;
  'aria-describedby'?: string;
  'aria-expanded'?: boolean;
  'aria-selected'?: boolean;
  'aria-disabled'?: boolean;
  'aria-invalid'?: boolean;
  'aria-required'?: boolean;
  'aria-current'?: boolean;
  'aria-busy'?: boolean;
}

export interface KeyboardNavigation {
  moveFocus: (direction: Direction) => void;
  selectNode: (nodeId: string) => void;
  selectEdge: (edgeId: string) => void;
  activatePanel: (panel: PanelType) => void;
  toggleKeyboardMode: () => void;
  resetNavigation: () => void;
}

export enum Direction {
  UP = 'UP',
  DOWN = 'DOWN',
  LEFT = 'LEFT',
  RIGHT = 'RIGHT',
}

export interface FocusManager {
  focusNode: (nodeId: string) => void;
  focusEdge: (edgeId: string) => void;
  focusPanel: (panel: PanelType) => void;
  clearFocus: () => void;
  getFocusableElements: () => HTMLElement[];
}

export interface AccessibilityContextType {
  state: AccessibilityState;
  navigation: KeyboardNavigation;
  focus: FocusManager;
  setIsKeyboardNavigation: (value: boolean) => void;
  setIsScreenReaderActive: (value: boolean) => void;
  setKeyboardMode: (mode: KeyboardMode) => void;
  setActivePanel: (panel: PanelType | null) => void;
}

export interface AccessibilityProviderProps {
  children: React.ReactNode;
  initialState?: Partial<AccessibilityState>;
}

export interface AccessibilityProviderState {
  state: AccessibilityState;
  previousState: AccessibilityState;
}

export interface AccessibilityConfig {
  keyboardShortcuts: Record<string, string>;
  ariaLabels: Record<string, string>;
  focusOrder: string[];
  panelOrder: PanelType[];
}
