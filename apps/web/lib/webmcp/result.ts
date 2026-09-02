// Tool result + input-validation helpers.
//
// WebMCP is treated as an external control interface (see docs/WEBMCP_CHALLENGE.md
// §10): every tool validates its input against a strict allow-list schema and
// returns clear, structured success/error results. We never surface stack traces,
// secrets, or internal details to the agent.

import type { JSONSchema, WebMCPToolResult } from './webmcp';

export type ErrorCode =
  | 'INVALID_INPUT'
  | 'PROJECT_NOT_FOUND'
  | 'GENERATION_FAILED'
  | 'DRAFT_FAILED'
  | 'EXPORT_NOT_READY'
  | 'EXPORT_REQUIRES_CONFIRMATION';

export function ok(data: unknown): WebMCPToolResult {
  return {
    content: [{ type: 'text', text: JSON.stringify(data) }],
    structuredContent: data
  };
}

export function fail(code: ErrorCode, message: string): WebMCPToolResult {
  const data = { error: code, message };
  return {
    content: [{ type: 'text', text: JSON.stringify(data) }],
    structuredContent: data,
    isError: true
  };
}

// A deliberately small, dependency-free validator for the subset of JSON Schema
// our tools use: object with typed properties, required, enum, string
// min/maxLength, and a "uri" format restricted to http/https. It rejects any
// property that is not declared (strict allow-list) so agents cannot smuggle in
// unexpected fields.
export interface FieldSpec {
  type: 'string' | 'boolean';
  required?: boolean;
  enum?: string[];
  minLength?: number;
  maxLength?: number;
  format?: 'uri';
  default?: unknown;
}

export type Spec = Record<string, FieldSpec>;

export function validate(
  input: unknown,
  spec: Spec
): { ok: true; value: Record<string, unknown> } | { ok: false; message: string } {
  if (input === null || typeof input !== 'object' || Array.isArray(input)) {
    return { ok: false, message: 'Input must be an object.' };
  }
  const obj = input as Record<string, unknown>;

  // Reject unknown keys (strict allow-list).
  for (const key of Object.keys(obj)) {
    if (!(key in spec)) return { ok: false, message: `Unknown field "${key}".` };
  }

  const out: Record<string, unknown> = {};
  for (const [key, field] of Object.entries(spec)) {
    let val = obj[key];
    if (val === undefined || val === null) {
      if (field.required) return { ok: false, message: `Missing required field "${key}".` };
      if (field.default !== undefined) out[key] = field.default;
      continue;
    }
    if (field.type === 'string') {
      if (typeof val !== 'string') return { ok: false, message: `"${key}" must be a string.` };
      val = val.trim();
      if (field.minLength !== undefined && (val as string).length < field.minLength) {
        return { ok: false, message: `"${key}" must be at least ${field.minLength} characters.` };
      }
      if (field.maxLength !== undefined && (val as string).length > field.maxLength) {
        return { ok: false, message: `"${key}" must be at most ${field.maxLength} characters.` };
      }
      if (field.enum && !field.enum.includes(val as string)) {
        return { ok: false, message: `"${key}" must be one of: ${field.enum.join(', ')}.` };
      }
      if (field.format === 'uri' && !isHttpUrl(val as string)) {
        return { ok: false, message: `"${key}" must be a valid http(s) URL.` };
      }
    } else if (field.type === 'boolean') {
      if (typeof val !== 'boolean') return { ok: false, message: `"${key}" must be a boolean.` };
    }
    out[key] = val;
  }
  return { ok: true, value: out };
}

// Only http/https URLs are accepted — no file:, javascript:, data:, etc.
export function isHttpUrl(value: string): boolean {
  try {
    const u = new URL(value);
    return u.protocol === 'http:' || u.protocol === 'https:';
  } catch {
    return false;
  }
}

// Build a JSON Schema object for registerTool from our compact spec, so the
// runtime advertises the same contract we enforce.
export function toJsonSchema(spec: Spec): JSONSchema {
  const properties: Record<string, unknown> = {};
  const required: string[] = [];
  for (const [key, field] of Object.entries(spec)) {
    const prop: Record<string, unknown> = {
      type: field.type === 'string' ? 'string' : 'boolean'
    };
    if (field.enum) prop.enum = field.enum;
    if (field.minLength !== undefined) prop.minLength = field.minLength;
    if (field.maxLength !== undefined) prop.maxLength = field.maxLength;
    if (field.format) prop.format = field.format;
    if (field.default !== undefined) prop.default = field.default;
    properties[key] = prop;
    if (field.required) required.push(key);
  }
  return { type: 'object', properties, required, additionalProperties: false };
}
