import { nanoid } from "nanoid";
import { z } from "zod";
import { protectedProcedure, publicProcedure, router } from "./_core/trpc";
import { respondAsDavid } from "./davidAgent";
import {
  createDavidMemory, createDavidProject, createDavidTask, deleteDavidMemory,
  getDavidConversationWithMessages, listDavidConversations, listDavidMemories, listDavidProjects, listDavidRunEvents, listDavidRuns, listDavidTasks,
  updateDavidProject, updateDavidTask,
} from "./db";

const projectStatus = z.enum(["active", "planning", "complete", "archived"]);
const taskStatus = z.enum(["todo", "in_progress", "blocked", "done"]);
const priority = z.enum(["low", "normal", "high"]);

export const davidRouter = router({
  status: publicProcedure.query(() => ({ runtime: "ready", model: "gpt-5-mini", streaming: true, personality: "David AI" })),
  chat: protectedProcedure.input(z.object({ message: z.string().trim().min(1).max(4000), conversationId: z.string().optional(), memoryIds: z.array(z.string()).max(12).optional() })).mutation(({ ctx, input }) => respondAsDavid({ userId: ctx.user.id, ...input })),
  conversations: router({
    list: protectedProcedure.query(({ ctx }) => listDavidConversations(ctx.user.id)),
    get: protectedProcedure.input(z.object({ id: z.string().min(1) })).query(({ ctx, input }) => getDavidConversationWithMessages(ctx.user.id, input.id)),
  }),
  memory: router({
    list: protectedProcedure.query(({ ctx }) => listDavidMemories(ctx.user.id)),
    create: protectedProcedure.input(z.object({ content: z.string().trim().min(1).max(3000), kind: z.enum(["fact", "preference", "decision", "learning", "note"]).default("note") })).mutation(({ ctx, input }) => createDavidMemory({ id: nanoid(), userId: ctx.user.id, content: input.content, kind: input.kind, source: "owner" })),
    delete: protectedProcedure.input(z.object({ id: z.string() })).mutation(({ ctx, input }) => deleteDavidMemory(ctx.user.id, input.id)),
  }),
  projects: router({
    list: protectedProcedure.query(({ ctx }) => listDavidProjects(ctx.user.id)),
    create: protectedProcedure.input(z.object({ name: z.string().trim().min(1).max(160), description: z.string().max(3000).optional() })).mutation(({ ctx, input }) => createDavidProject({ id: nanoid(), userId: ctx.user.id, name: input.name, description: input.description ?? null, status: "active" })),
    update: protectedProcedure.input(z.object({ id: z.string(), name: z.string().trim().min(1).max(160).optional(), description: z.string().max(3000).nullable().optional(), status: projectStatus.optional() })).mutation(({ ctx, input }) => updateDavidProject(ctx.user.id, input.id, input)),
  }),
  tasks: router({
    list: protectedProcedure.query(({ ctx }) => listDavidTasks(ctx.user.id)),
    create: protectedProcedure.input(z.object({ title: z.string().trim().min(1).max(240), description: z.string().max(3000).optional(), projectId: z.string().nullable().optional(), priority: priority.default("normal") })).mutation(({ ctx, input }) => createDavidTask({ id: nanoid(), userId: ctx.user.id, title: input.title, description: input.description ?? null, projectId: input.projectId ?? null, priority: input.priority, status: "todo" })),
    update: protectedProcedure.input(z.object({ id: z.string(), title: z.string().trim().min(1).max(240).optional(), description: z.string().max(3000).nullable().optional(), projectId: z.string().nullable().optional(), priority: priority.optional(), status: taskStatus.optional() })).mutation(({ ctx, input }) => updateDavidTask(ctx.user.id, input.id, input)),
  }),
  runs: router({ list: protectedProcedure.query(({ ctx }) => listDavidRuns(ctx.user.id)), events: protectedProcedure.input(z.object({ runId: z.string() })).query(({ ctx, input }) => listDavidRunEvents(ctx.user.id, input.runId)) }),
});
