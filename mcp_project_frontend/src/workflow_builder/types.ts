import type { AIComponent } from '../types/index';

export type ComponentPaletteProps = {};

// Re-export AIComponent type for convenience
export type { AIComponent } from '../types/index';

export type PaletteItemProps = {
  component: AIComponent;
};
