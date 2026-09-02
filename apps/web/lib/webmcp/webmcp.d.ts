// Minimal ambient typing for the WebMCP browser API (document.modelContext).
//
// The runtime is provided natively by Chrome 149+ (chrome://flags/#enable-webmcp-testing)
// and the ChatGPT desktop browser, and is polyfilled by @mcp-b/webmcp-polyfill in
// every other browser. The polyfill package does not ship a global augmentation
// for `document.modelContext`, so we declare the small surface we use here.

export type JSONSchema = Record<string, unknown>;

// A WebMCP tool result follows the MCP CallToolResult shape.
export interface WebMCPToolResult {
  content: { type: 'text'; text: string }[];
  structuredContent?: unknown;
  isError?: boolean;
}

export interface WebMCPToolDescriptor {
  name: string;
  description: string;
  title?: string;
  inputSchema?: JSONSchema;
  execute: (input: unknown) => Promise<WebMCPToolResult>;
  annotations?: Record<string, unknown>;
}

interface ModelContext {
  registerTool(
    tool: WebMCPToolDescriptor,
    options?: { signal?: AbortSignal }
  ): void | Promise<void>;
}

declare global {
  interface Document {
    modelContext?: ModelContext;
  }
  interface Navigator {
    modelContext?: ModelContext;
  }
}
