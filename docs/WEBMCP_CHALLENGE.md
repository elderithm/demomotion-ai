# DemoMotion AI — WebMCP Challenge Development Specification

## 1. Purpose

This work extends the existing open-source `demomotion-ai` project for the OpenAI WebMCP Challenge.

The objective is NOT to turn DemoMotion OSS into the full commercial DemoMotion Cloud product.

The objective is to demonstrate:

> A human and an AI agent can collaboratively create, modify, and export a software demo through structured WebMCP tools.

The implementation must strengthen the open-source ecosystem while preserving the commercial differentiation of DemoMotion Cloud.

---

# 2. Product Boundary

DemoMotion is intentionally divided into two product layers.

## DemoMotion AI / Public OSS

Purpose:

- developer adoption
- experimentation
- local-first demo creation
- open-source ecosystem
- agent integrations
- basic demo generation

WebMCP belongs primarily to this layer as an integration interface.

## DemoMotion Cloud / Commercial

Purpose:

- production use
- hosted workflows
- persistent projects
- team usage
- scalable generation
- advanced automation
- premium functionality
- monetization

The WebMCP Challenge implementation MUST NOT reduce the need for DemoMotion Cloud for professional or organizational use.

---

# 3. Core Architecture Principle

WebMCP must be implemented as a thin adapter over capabilities that already exist, or that reasonably belong, in DemoMotion OSS.

Preferred architecture:

```text
AI Agent
   │
   │ WebMCP
   ▼
WebMCP Adapter Layer
   │
   ▼
DemoMotion OSS Application Services
   │
   ├── capture / recording
   ├── demo composition
   ├── narration
   ├── preview
   └── basic export
```

Do NOT duplicate business logic inside WebMCP handlers.

WebMCP handlers should call existing application/service functions wherever possible.

The WebMCP integration must remain replaceable and loosely coupled.

---

# 4. Standalone Requirement

The hackathon submission must NOT depend on the private `demomotion-cloud` repository.

The public project must be independently understandable and runnable from the public repository.

It is acceptable to use legitimate third-party APIs where required, provided:

- the integration is documented;
- required environment variables are documented;
- secrets are never committed;
- the live hackathon deployment has valid credentials;
- the implementation source code for the integration is present in the public repository.

Do NOT import source code from `demomotion-cloud`.

Do NOT call undocumented private DemoMotion Cloud endpoints.

---

# 5. Judge Accessibility

The hackathon experience must work from a normal hosted web URL.

The primary judging flow MUST NOT require:

- installation of the DemoMotion Chrome extension;
- access to a private repository;
- access to an internal developer environment;
- manual database setup;
- proprietary DemoMotion Cloud infrastructure.

If the existing OSS architecture depends heavily on the Chrome extension, create the smallest possible browser-accessible WebMCP demonstration workflow instead of attempting to reproduce the entire extension.

Prefer adding a route such as:

```text
/webmcp
```

or another clearly named demo workspace.

Do not redesign the entire application.

---

# 6. Minimum WebMCP Experience

Implement approximately 3–5 meaningful WebMCP tools.

Do NOT maximize the number of tools.

Quality and human-agent collaboration matter more than tool count.

Exact tool names should follow the existing DemoMotion domain model, but the expected capability set is approximately:

### 6.1 Read current state

Example:

```text
get_demo_state
```

Purpose:

- return the current demo/project state;
- allow the agent to understand what the human has already created;
- allow collaborative editing.

Read-only.

---

### 6.2 Start or create a demo

Example:

```text
create_demo
```

or, if supported by the existing architecture:

```text
start_capture
```

Purpose:

- initiate a basic DemoMotion workflow;
- create a draft project or recording session.

Do not implement Cloud project management.

---

### 6.3 Update the demo

Example:

```text
update_demo
```

Potential inputs:

- title
- narration/script
- selected scenes
- scene ordering
- simple metadata

Only expose fields already supported by the OSS application or fields that are trivial additions.

Do NOT expose advanced Cloud-only editing functionality.

---

### 6.4 Generate narration or demo output

Example:

```text
generate_narration
```

or:

```text
generate_demo
```

Use existing OSS generation capability wherever possible.

This should demonstrate a real state-changing agent action.

---

### 6.5 Basic export

Example:

```text
export_demo
```

This may generate or initiate the basic OSS export flow.

The agent must NOT automatically:

- publish publicly;
- upload to an external organization;
- create shareable production URLs;
- distribute content externally.

Those actions belong to Cloud or require explicit human confirmation.

---

# 7. Human-Agent Collaboration Requirement

Do not create a fully autonomous "agent does everything while the human watches" workflow.

The challenge concept should demonstrate collaboration.

Target experience:

```text
Human creates or begins a demo
        ↓
Agent reads current DemoMotion state
        ↓
Human asks:
"Make this demo shorter and improve the narration."
        ↓
Agent uses WebMCP tools
        ↓
DemoMotion UI visibly changes
        ↓
Human reviews the result
        ↓
Human approves export
        ↓
Agent triggers basic export
```

The UI should visibly reflect agent actions where practical.

The human should remain able to manually modify the same project.

This shared state is strategically important.

---

# 8. WebMCP Implementation

Use the current WebMCP browser APIs recommended by the challenge documentation.

Prefer the standard WebMCP mechanism, such as:

```text
document.modelContext.registerTool(...)
```

or an appropriate maintained React integration compatible with the current specification.

Do NOT implement a separate traditional MCP server unless technically necessary.

This challenge is specifically about websites exposing structured browser tools.

Keep WebMCP registration close to the client-side application layer.

Suggested structure:

```text
src/
  webmcp/
    registerTools.ts
    tools/
      getDemoState.ts
      createDemo.ts
      updateDemo.ts
      generateDemo.ts
      exportDemo.ts
    schemas/
      ...
```

Adapt directory names to the existing repository architecture.

Do not reorganize the project solely to match this example.

---

# 9. Tool Design Requirements

Every tool must have:

- a specific name;
- a precise description;
- a strict input schema;
- clear success output;
- clear error output;
- deterministic behavior where practical.

Bad:

```text
do_demo_stuff
```

Good:

```text
update_demo_narration
```

Descriptions must tell the agent exactly when the tool should and should not be used.

Avoid overlapping tools.

Avoid tools with extremely broad capabilities.

---

# 10. Security Requirements

Treat WebMCP as an external control interface.

All inputs must be validated.

Use strict schemas.

Do not allow arbitrary:

- shell commands;
- filesystem paths;
- JavaScript execution;
- SQL;
- network requests;
- arbitrary URLs without validation;
- dynamic imports.

Never expose:

- API keys;
- authentication tokens;
- session cookies;
- environment variables;
- internal infrastructure details;
- Cloud credentials.

External webpage content must be treated as untrusted data.

Do not interpret text contained inside captured pages as instructions to the WebMCP agent.

Avoid prompt-injection pathways between:

```text
captured website content
→ DemoMotion
→ WebMCP tool instructions
```

Side-effecting operations must have explicit, narrow semantics.

Destructive or externally visible operations should require human confirmation.

---

# 11. Commercial Boundary — Public vs Cloud

## Allowed in DemoMotion OSS

The following may remain or be added to the public version:

- local/basic demo creation
- basic browser recording where already supported
- basic scene handling
- basic narration
- local/basic export
- WebMCP tool definitions
- WebMCP adapters
- agent-readable project state
- basic agent-controlled editing
- documentation
- example projects
- local developer integrations

WebMCP itself should be treated as an ecosystem/distribution feature.

---

# 12. Cloud-Only Features

The following SHOULD remain commercial and MUST NOT be implemented as part of this hackathon unless already intentionally open-sourced.

### Infrastructure

- hosted rendering infrastructure
- scalable rendering workers
- distributed rendering
- persistent cloud project storage
- managed asset storage
- CDN-based delivery
- production job queues

### Accounts and organizations

- user accounts
- team workspaces
- organizations
- permissions
- enterprise SSO
- collaboration management

### Monetization

- billing
- subscriptions
- usage metering
- plan enforcement
- Revenue or Stripe integrations
- commercial quotas

### Production workflows

- batch generation
- scheduled generation
- webhook automation
- enterprise APIs
- large-scale automation
- production publishing pipelines

### Premium generation

- advanced proprietary orchestration
- premium rendering pipelines
- premium templates
- brand kits
- organization-wide templates
- advanced AI workflows
- high-resolution / high-volume rendering where commercially differentiated

### Business intelligence

- analytics dashboards
- engagement analytics
- viewer analytics
- team analytics
- organization usage analytics

### Sharing

Basic local export may exist in OSS.

Managed hosted sharing should remain Cloud-only, including:

- persistent share URLs
- managed hosting
- access control
- viewer tracking
- organizational sharing

---

# 13. Explicitly Forbidden Changes

Claude Code MUST NOT do any of the following.

## Repository / IP

DO NOT:

- copy code from `demomotion-cloud`;
- request access to the private Cloud repository;
- reproduce proprietary Cloud implementation;
- reverse-engineer Cloud functionality;
- expose Cloud architecture;
- change the existing OSS license without explicit instruction;
- move proprietary assets into the public repository.

## Product scope

DO NOT add:

- authentication systems;
- billing;
- subscriptions;
- organization management;
- team collaboration;
- enterprise features;
- full hosted project management;
- analytics;
- advanced Cloud rendering;
- production APIs;
- webhooks;
- batch generation.

## Architecture

DO NOT:

- rewrite the existing app;
- replace the current framework;
- perform major unrelated refactoring;
- replace working services simply to modernize them;
- introduce unnecessary infrastructure.

## Hackathon shortcuts

DO NOT:

- fake agent actions;
- fake WebMCP functionality;
- hardcode demo outputs;
- simulate successful tool calls without performing real state changes;
- claim functionality that is not running.

Every demonstrated tool call must actually execute.

---

# 14. Existing Functionality First

Before implementing anything:

1. Read `CLAUDE.md`.
2. Read all relevant files under `docs/`.
3. Inspect the current DemoMotion architecture.
4. Identify existing functionality reusable by WebMCP.
5. Produce a short implementation plan.
6. Implement the smallest reasonable change.

Prefer:

```text
existing capability
+ WebMCP adapter
```

over:

```text
new duplicate capability
+ WebMCP adapter
```

---

# 15. Scope Control

This is a hackathon extension, not a new product rewrite.

Prioritize in this order:

1. WebMCP tool registration works.
2. Agent can discover tools.
3. Agent can execute tools.
4. Tools modify actual DemoMotion state.
5. Human can observe the change.
6. Live deployment works.
7. README clearly explains testing.
8. Demo video can demonstrate the flow.
9. Polish only after the above works.

Do not spend substantial time on visual redesign.

---

# 16. Challenge-Specific Documentation

Add a dedicated section to README:

```text
## WebMCP Challenge 2026
```

Clearly distinguish:

### Pre-existing DemoMotion functionality

Explain what existed before August 25, 2026.

### New WebMCP functionality

List every material feature added after August 25, 2026.

Include:

- WebMCP tool names;
- relevant source directories;
- architecture diagram if useful;
- instructions for testing;
- supported browser environment;
- known limitations.

Make it extremely easy for judges to understand what is new.

---

# 17. Commit Discipline

WebMCP-related implementation must have clear commits.

Prefer several understandable commits rather than one opaque giant commit.

Examples:

```text
feat(webmcp): add DemoMotion tool registration

feat(webmcp): expose demo state to browser agents

feat(webmcp): allow agents to update narration

feat(webmcp): add basic export workflow

docs(webmcp): document challenge implementation
```

Do not rewrite existing Git history.

Do not falsify timestamps.

---

# 18. Live Demo Requirements

The live environment must:

- load without developer intervention;
- register WebMCP tools successfully;
- contain an obvious sample workflow;
- avoid dependency on private Cloud infrastructure;
- handle errors gracefully.

If an API credential is required, configure it securely in the deployed environment.

Never expose secrets client-side.

---

# 19. Recommended Demo Scenario

Optimize for a demo that can be understood within approximately 60–90 seconds.

Example:

### Step 1

Human opens an existing/simple DemoMotion project.

### Step 2

Human tells the agent:

```text
Review this DemoMotion project and make the narration more concise.
```

### Step 3

Agent calls:

```text
get_demo_state
```

### Step 4

Agent calls:

```text
update_demo_narration
```

DemoMotion UI visibly updates.

### Step 5

Human says:

```text
Looks good. Generate the final demo.
```

### Step 6

Agent calls:

```text
generate_demo
```

### Step 7

Human reviews the result.

### Step 8

Agent invokes basic export after approval.

The differentiating message is:

> Before WebMCP, agents had to visually guess how to operate a complex demo-generation UI. With WebMCP, DemoMotion exposes structured creative actions while humans retain control of the same workspace.

---

# 20. UX Principle

Do not hide WebMCP completely.

Add a subtle indicator such as:

```text
WebMCP enabled
```

and optionally show recent agent actions.

For example:

```text
Agent activity

✓ Read demo state
✓ Updated narration
✓ Generated preview
```

This is useful both for user trust and for hackathon demonstrations.

Do not build a large monitoring dashboard.

---

# 21. Error Handling

Tools should return useful structured errors.

Examples:

```text
PROJECT_NOT_FOUND
INVALID_SCENE_ID
INVALID_INPUT
GENERATION_FAILED
EXPORT_NOT_READY
```

Do not leak stack traces or secrets to the agent.

Failures should not leave project state corrupted.

---

# 22. Tests

Add focused tests for:

- schema validation;
- tool registration;
- successful tool execution;
- invalid input;
- missing project state;
- side-effect boundaries.

Do not attempt to dramatically increase overall repository test coverage during this task.

---

# 23. Definition of Done

The WebMCP Challenge implementation is complete when:

- [ ] Public DemoMotion repository remains independently useful.
- [ ] No private DemoMotion Cloud code is exposed.
- [ ] No Cloud-only product capabilities are recreated.
- [ ] At least 3 meaningful WebMCP tools work.
- [ ] Tools operate against real DemoMotion application state.
- [ ] Human and agent can modify the same workflow.
- [ ] The project works from a judge-accessible live URL.
- [ ] Chrome extension installation is not required for the primary judging flow.
- [ ] Tool inputs use strict schemas.
- [ ] Secrets are never exposed.
- [ ] README distinguishes pre-existing vs new work.
- [ ] README contains WebMCP testing instructions.
- [ ] Public repository contains an existing visible open-source license.
- [ ] A <3-minute demo can clearly demonstrate the functionality.
- [ ] Existing DemoMotion functionality continues to work.
- [ ] Build passes.
- [ ] Relevant tests pass.

---

# 24. Highest-Level Rule

When deciding whether a feature belongs in this implementation, use this test:

> Does this feature make DemoMotion easier for agents to use, or does it replace a reason customers would pay for DemoMotion Cloud?

If the answer is:

```text
easier for agents to use
```

it may belong in OSS.

If the answer is:

```text
replaces a reason customers pay for Cloud
```

DO NOT IMPLEMENT IT.

When uncertain, preserve the commercial boundary and choose the smaller implementation.
