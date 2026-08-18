import { nanoid } from "nanoid";
import { invokeLLM, listLLMModels, streamLLM, type Message } from "./_core/llm";
import {
  createDavidMemory,
  createDavidProject,
  createDavidTask,
  createDavidConversation,
  createDavidRunEvent,
  createDavidMessage,
  createDavidRun,
  getDavidConversation,
  listDavidMemoriesByIds,
  listDavidMessages,
  updateDavidRun,
} from "./db";

export const DAVID_SYSTEM_PROMPT = `You are David AI, a personal AI operating system and intelligent assistant. You speak with a calm, professional British tone similar to JARVIS. You help your owner David with planning, research, creative work, business operations, and any task requested. You are proactive, concise, and always truthful about what you can and cannot do. You remember context from the conversation and build on previous interactions.

You are an assistant, not a fictional character. Do not claim to have used tools, sent messages, created files, visited websites, or completed external work unless evidence supplied in the conversation proves it. For multi-step work, state a concise numbered plan and identify any action that needs confirmation. Use Markdown where it improves clarity.`;

const preferredModel = async () => {
  const catalog = await listLLMModels();
  const ids = catalog.data.map((model) => model.id);
  return ids.includes("gpt-5-mini") ? "gpt-5-mini" : ids[0];
};

export type DavidWorkspaceDecision = {
  intent: "none" | "save_memory" | "create_project" | "create_task";
  memoryContent: string | null;
  projectName: string | null;
  projectDescription: string | null;
  taskTitle: string | null;
  taskDescription: string | null;
  taskPriority: "low" | "normal" | "high" | null;
};

export type DavidPlanArtifact = {
  isMultiStep: boolean;
  steps: string[];
};

const planArtifactSchema = {
  type: "object",
  properties: {
    isMultiStep: { type: "boolean" },
    steps: { type: "array", items: { type: "string" }, minItems: 1, maxItems: 6 },
  },
  required: ["isMultiStep", "steps"],
  additionalProperties: false,
} as const;

export function parsePlanArtifact(value: string): DavidPlanArtifact {
  try {
    const parsed = JSON.parse(value) as Record<string, unknown>;
    const steps = Array.isArray(parsed.steps) ? parsed.steps.filter((step): step is string => typeof step === "string" && Boolean(step.trim())).map((step) => step.trim()).slice(0, 6) : [];
    return { isMultiStep: parsed.isMultiStep === true, steps: steps.length ? steps : ["Respond clearly with the available context."] };
  } catch {
    return { isMultiStep: false, steps: ["Respond clearly with the available context."] };
  }
}

function formatPlan(plan: DavidPlanArtifact) {
  return plan.steps.map((step, index) => `${index + 1}. ${step}`).join("\n");
}

const workspaceDecisionSchema = {
  type: "object",
  properties: {
    intent: { type: "string", enum: ["none", "save_memory", "create_project", "create_task"] },
    memoryContent: { type: ["string", "null"] },
    projectName: { type: ["string", "null"] },
    projectDescription: { type: ["string", "null"] },
    taskTitle: { type: ["string", "null"] },
    taskDescription: { type: ["string", "null"] },
    taskPriority: { type: ["string", "null"], enum: ["low", "normal", "high", null] },
  },
  required: ["intent", "memoryContent", "projectName", "projectDescription", "taskTitle", "taskDescription", "taskPriority"],
  additionalProperties: false,
} as const;

const emptyWorkspaceDecision: DavidWorkspaceDecision = { intent: "none", memoryContent: null, projectName: null, projectDescription: null, taskTitle: null, taskDescription: null, taskPriority: null };

function cleanNullableString(value: unknown) {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

export function parseWorkspaceDecision(value: string): DavidWorkspaceDecision {
  try {
    const parsed = JSON.parse(value) as Record<string, unknown>;
    const intent = parsed.intent;
    if (intent !== "save_memory" && intent !== "create_project" && intent !== "create_task" && intent !== "none") return emptyWorkspaceDecision;
    return {
      intent,
      memoryContent: cleanNullableString(parsed.memoryContent),
      projectName: cleanNullableString(parsed.projectName),
      projectDescription: cleanNullableString(parsed.projectDescription),
      taskTitle: cleanNullableString(parsed.taskTitle),
      taskDescription: cleanNullableString(parsed.taskDescription),
      taskPriority: parsed.taskPriority === "low" || parsed.taskPriority === "normal" || parsed.taskPriority === "high" ? parsed.taskPriority : null,
    };
  } catch {
    return emptyWorkspaceDecision;
  }
}

async function decideWorkspaceAction(model: string, message: string): Promise<DavidWorkspaceDecision> {
  try {
    const response = await invokeLLM({
      model,
      messages: [
        { role: "system", content: "Classify whether the user explicitly instructs David AI to save a memory, create a project, or create a task. Select an action only for a direct, unambiguous request. Never create anything for a question, suggestion, plan, or implied goal. Return none when uncertain." },
        { role: "user", content: message },
      ],
      response_format: { type: "json_schema", json_schema: { name: "david_workspace_action", strict: true, schema: workspaceDecisionSchema } },
      maxTokens: 350,
    });
    return parseWorkspaceDecision(typeof response.choices[0]?.message.content === "string" ? response.choices[0].message.content : "");
  } catch {
    return emptyWorkspaceDecision;
  }
}

async function applyWorkspaceAction(userId: number, decision: DavidWorkspaceDecision): Promise<string | null> {
  if (decision.intent === "save_memory" && decision.memoryContent) {
    await createDavidMemory({ id: nanoid(), userId, kind: "note", content: decision.memoryContent, source: "David AI chat" });
    return `Server-confirmed workspace action: saved a memory — “${decision.memoryContent}”.`;
  }
  if (decision.intent === "create_project" && decision.projectName) {
    await createDavidProject({ id: nanoid(), userId, name: decision.projectName, description: decision.projectDescription, status: "active" });
    return `Server-confirmed workspace action: created project “${decision.projectName}”.`;
  }
  if (decision.intent === "create_task" && decision.taskTitle) {
    await createDavidTask({ id: nanoid(), userId, projectId: null, title: decision.taskTitle, description: decision.taskDescription, status: "todo", priority: decision.taskPriority ?? "normal" });
    return `Server-confirmed workspace action: created task “${decision.taskTitle}”.`;
  }
  return null;
}

async function generatePlanArtifact(model: string, message: string): Promise<DavidPlanArtifact> {
  try {
    const response = await invokeLLM({
      model,
      messages: [
        { role: "system", content: "Create a concise, truthful response plan. Mark isMultiStep true only when the request benefits from multiple distinct stages. Steps must describe analysis or communication only; never state that an external action has occurred." },
        { role: "user", content: message },
      ],
      response_format: { type: "json_schema", json_schema: { name: "david_plan_artifact", strict: true, schema: planArtifactSchema } },
      maxTokens: 400,
    });
    return parsePlanArtifact(typeof response.choices[0]?.message.content === "string" ? response.choices[0].message.content : "");
  } catch {
    return { isMultiStep: false, steps: ["Respond clearly with the available context."] };
  }
}

export function composeDavidMessages(params: { history: Array<{ role: "user" | "assistant"; content: string }>; memories: Array<{ kind: string; content: string }> }): Message[] {
  const memoryContext = params.memories.slice(0, 12).map((memory) => `- ${memory.kind}: ${memory.content}`).join("\n");
  return [
    { role: "system", content: DAVID_SYSTEM_PROMPT },
    ...(memoryContext ? [{ role: "system" as const, content: `Approved owner context:\n${memoryContext}` }] : []),
    ...params.history.map((message) => ({ role: message.role, content: message.content })),
  ];
}

export type DavidLifecycleEvent = {
  id: string;
  runId: string;
  type: "goal_received" | "plan_created" | "model_selected" | "response_streaming" | "verification_started" | "verification_passed" | "run_degraded" | "run_failed";
  state: "planning" | "thinking" | "executing" | "verifying" | "complete" | "degraded" | "failed";
  actor: string;
  summary: string;
  provider?: string | null;
};

async function prepareRun(userId: number, message: string, conversationId?: string, onEvent?: (event: DavidLifecycleEvent) => void, memoryIds: string[] = []) {
  let resolvedConversationId = conversationId;
  if (resolvedConversationId) {
    const existing = await getDavidConversation(userId, resolvedConversationId);
    if (!existing) resolvedConversationId = undefined;
  }
  if (!resolvedConversationId) {
    resolvedConversationId = nanoid();
    await createDavidConversation(userId, resolvedConversationId, message.slice(0, 80));
  }
  await createDavidMessage({ id: nanoid(), userId, conversationId: resolvedConversationId, role: "user", content: message });
  const runId = nanoid();
  await createDavidRun({ id: runId, userId, conversationId: resolvedConversationId, objective: message, status: "planning", plan: "David is preparing a context-aware response.", planData: null, provider: null });
  const goalEvent: DavidLifecycleEvent = { id: nanoid(), runId, type: "goal_received", state: "planning", actor: "David AI", summary: "Goal received and run created." };
  await createDavidRunEvent({ ...goalEvent, userId, provider: null, metadata: null });
  onEvent?.(goalEvent);
  const planEvent: DavidLifecycleEvent = { id: nanoid(), runId, type: "plan_created", state: "planning", actor: "David AI", summary: "Context and response plan are being assembled." };
  await createDavidRunEvent({ ...planEvent, userId, provider: null, metadata: null });
  onEvent?.(planEvent);
  const [history, memories] = await Promise.all([listDavidMessages(userId, resolvedConversationId), listDavidMemoriesByIds(userId, memoryIds)]);
  return { conversationId: resolvedConversationId, runId, history, memories };
}

export async function respondAsDavid(params: { userId: number; message: string; conversationId?: string; memoryIds?: string[] }) {
  const prepared = await prepareRun(params.userId, params.message, params.conversationId, undefined, params.memoryIds);
  try {
    const model = await preferredModel();
    const plan = await generatePlanArtifact(model, params.message);
    const planText = formatPlan(plan);
    await updateDavidRun(params.userId, prepared.runId, { status: "planning", provider: model, plan: planText, planData: JSON.stringify(plan) });
    const workspaceNote = await applyWorkspaceAction(params.userId, await decideWorkspaceAction(model, params.message));
    const response = await invokeLLM({ model, messages: [...composeDavidMessages({ history: prepared.history, memories: prepared.memories }), { role: "system" as const, content: `Response plan:\n${planText}` }, ...(workspaceNote ? [{ role: "system" as const, content: workspaceNote }] : [])], maxTokens: 1200, reasoning: { effort: "low" } });
    const responseText = typeof response.choices[0]?.message.content === "string" ? response.choices[0].message.content : "I’m sorry, David. I could not produce a readable response.";
    const content = `${responseText}${workspaceNote ? `\n\n${workspaceNote}` : ""}`;
    await createDavidMessage({ id: nanoid(), userId: params.userId, conversationId: prepared.conversationId, role: "assistant", content, model });
    await updateDavidRun(params.userId, prepared.runId, { status: "complete", provider: model, plan: "Response generated from the current conversation and approved memories." });
    return { ...prepared, content, model, state: "complete" as const };
  } catch (error) {
    await updateDavidRun(params.userId, prepared.runId, { status: "failed", plan: error instanceof Error ? error.message.slice(0, 1000) : "David could not reach the language model." });
    throw error;
  }
}

export async function streamAsDavid(params: { userId: number; message: string; conversationId?: string; memoryIds?: string[]; onToken: (token: string) => void; onEvent?: (event: DavidLifecycleEvent) => void }) {
  const prepared = await prepareRun(params.userId, params.message, params.conversationId, params.onEvent, params.memoryIds);
  try {
    const model = await preferredModel();
    const plan = await generatePlanArtifact(model, params.message);
    const planText = formatPlan(plan);
    await updateDavidRun(params.userId, prepared.runId, { status: "planning", provider: model, plan: planText, planData: JSON.stringify(plan) });
    const planEvent: DavidLifecycleEvent = { id: nanoid(), runId: prepared.runId, type: "plan_created", state: "planning", actor: "David AI", summary: plan.isMultiStep ? `Generated a ${plan.steps.length}-step response plan.` : "Generated a focused response plan.", provider: model };
    await createDavidRunEvent({ ...planEvent, userId: params.userId, provider: model, metadata: null });
    params.onEvent?.(planEvent);
    const workspaceNote = await applyWorkspaceAction(params.userId, await decideWorkspaceAction(model, params.message));
    const modelEvent: DavidLifecycleEvent = { id: nanoid(), runId: prepared.runId, type: "model_selected", state: "thinking", actor: "David AI", summary: "Reasoning model selected for this response.", provider: model };
    await createDavidRunEvent({ ...modelEvent, userId: params.userId, provider: model, metadata: null });
    params.onEvent?.(modelEvent);
    let content = "";
    const streamingEvent: DavidLifecycleEvent = { id: nanoid(), runId: prepared.runId, type: "response_streaming", state: "executing", actor: "David AI", summary: "David is composing a streamed response.", provider: model };
    await createDavidRunEvent({ ...streamingEvent, userId: params.userId, provider: model, metadata: null });
    params.onEvent?.(streamingEvent);
    for await (const token of streamLLM({ model, messages: [...composeDavidMessages({ history: prepared.history, memories: prepared.memories }), { role: "system" as const, content: `Response plan:\n${planText}` }, ...(workspaceNote ? [{ role: "system" as const, content: workspaceNote }] : [])], maxTokens: 1200, reasoning: { effort: "low" } })) {
      content += token;
      params.onToken(token);
    }
    const finalContent = `${content || "I’m sorry, David. I could not produce a readable response."}${workspaceNote ? `\n\n${workspaceNote}` : ""}`;
    if (workspaceNote) params.onToken(`\n\n${workspaceNote}`);
    await createDavidMessage({ id: nanoid(), userId: params.userId, conversationId: prepared.conversationId, role: "assistant", content: finalContent, model });
    const verifyingEvent: DavidLifecycleEvent = { id: nanoid(), runId: prepared.runId, type: "verification_started", state: "verifying", actor: "David AI", summary: "Response persistence and delivery are being verified.", provider: model };
    await createDavidRunEvent({ ...verifyingEvent, userId: params.userId, provider: model, metadata: null });
    params.onEvent?.(verifyingEvent);
    await updateDavidRun(params.userId, prepared.runId, { status: "complete", provider: model, plan: planText });
    const completeEvent: DavidLifecycleEvent = { id: nanoid(), runId: prepared.runId, type: "verification_passed", state: "complete", actor: "David AI", summary: "Response was persisted and is ready for review.", provider: model };
    await createDavidRunEvent({ ...completeEvent, userId: params.userId, provider: model, metadata: null });
    params.onEvent?.(completeEvent);
    return { ...prepared, content: finalContent, model, state: "complete" as const };
  } catch (error) {
    await updateDavidRun(params.userId, prepared.runId, { status: "failed", plan: error instanceof Error ? error.message.slice(0, 1000) : "David could not reach the language model." });
    const failureEvent: DavidLifecycleEvent = { id: nanoid(), runId: prepared.runId, type: "run_failed", state: "failed", actor: "David AI", summary: error instanceof Error ? error.message.slice(0, 500) : "David could not reach the language model." };
    await createDavidRunEvent({ ...failureEvent, userId: params.userId, provider: null, metadata: null });
    params.onEvent?.(failureEvent);
    throw error;
  }
}
