import { and, desc, eq, inArray } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import {
  DavidConversation,
  DavidMemory,
  DavidProject,
  DavidRun,
  DavidRunEvent,
  DavidTask,
  InsertUser,
  davidConversations,
  davidMemories,
  davidMessages,
  davidProjects,
  davidRuns,
  davidRunEvents,
  davidTasks,
  users,
} from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

// Lazily create the drizzle instance so local tooling can run without a DB.
export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = 'admin';
      updateSet.role = 'admin';
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);

  return result.length > 0 ? result[0] : undefined;
}

async function workspaceDb() {
  const db = await getDb();
  if (!db) throw new Error("David AI storage is not available. Please try again shortly.");
  return db;
}

export async function listDavidMemories(userId: number): Promise<DavidMemory[]> {
  const db = await workspaceDb();
  return db.select().from(davidMemories).where(eq(davidMemories.userId, userId)).orderBy(desc(davidMemories.updatedAt));
}

export async function listDavidMemoriesByIds(userId: number, ids: string[]): Promise<DavidMemory[]> {
  if (ids.length === 0) return [];
  const db = await workspaceDb();
  return db.select().from(davidMemories).where(and(eq(davidMemories.userId, userId), inArray(davidMemories.id, ids))).orderBy(desc(davidMemories.updatedAt));
}

export async function createDavidMemory(input: Omit<DavidMemory, "createdAt" | "updatedAt">) {
  const db = await workspaceDb();
  await db.insert(davidMemories).values(input);
  return input;
}

export async function deleteDavidMemory(userId: number, id: string) {
  const db = await workspaceDb();
  await db.delete(davidMemories).where(and(eq(davidMemories.userId, userId), eq(davidMemories.id, id)));
}

export async function listDavidProjects(userId: number): Promise<DavidProject[]> {
  const db = await workspaceDb();
  return db.select().from(davidProjects).where(eq(davidProjects.userId, userId)).orderBy(desc(davidProjects.updatedAt));
}

export async function createDavidProject(input: Omit<DavidProject, "createdAt" | "updatedAt">) {
  const db = await workspaceDb();
  await db.insert(davidProjects).values(input);
  return input;
}

export async function updateDavidProject(userId: number, id: string, patch: Partial<Pick<DavidProject, "name" | "description" | "status">>) {
  const db = await workspaceDb();
  await db.update(davidProjects).set(patch).where(and(eq(davidProjects.userId, userId), eq(davidProjects.id, id)));
}

export async function listDavidTasks(userId: number): Promise<DavidTask[]> {
  const db = await workspaceDb();
  return db.select().from(davidTasks).where(eq(davidTasks.userId, userId)).orderBy(desc(davidTasks.updatedAt));
}

export async function createDavidTask(input: Omit<DavidTask, "createdAt" | "updatedAt">) {
  const db = await workspaceDb();
  await db.insert(davidTasks).values(input);
  return input;
}

export async function updateDavidTask(userId: number, id: string, patch: Partial<Pick<DavidTask, "title" | "description" | "status" | "priority" | "projectId">>) {
  const db = await workspaceDb();
  await db.update(davidTasks).set(patch).where(and(eq(davidTasks.userId, userId), eq(davidTasks.id, id)));
}

export async function listDavidConversations(userId: number): Promise<DavidConversation[]> {
  const db = await workspaceDb();
  return db.select().from(davidConversations).where(eq(davidConversations.userId, userId)).orderBy(desc(davidConversations.updatedAt));
}

export async function createDavidConversation(userId: number, id: string, title: string) {
  const db = await workspaceDb();
  const item = { id, userId, title };
  await db.insert(davidConversations).values(item);
  return item;
}

export async function getDavidConversation(userId: number, id: string) {
  const db = await workspaceDb();
  const rows = await db.select().from(davidConversations).where(and(eq(davidConversations.userId, userId), eq(davidConversations.id, id))).limit(1);
  return rows[0];
}

export async function getDavidConversationWithMessages(userId: number, id: string) {
  const conversation = await getDavidConversation(userId, id);
  if (!conversation) return undefined;
  const messages = await listDavidMessages(userId, id, 100);
  return { ...conversation, messages };
}

export async function listDavidMessages(userId: number, conversationId: string, limit = 18) {
  const db = await workspaceDb();
  const rows = await db.select().from(davidMessages).where(and(eq(davidMessages.userId, userId), eq(davidMessages.conversationId, conversationId))).orderBy(desc(davidMessages.createdAt)).limit(limit);
  return rows.reverse();
}

export async function createDavidMessage(input: { id: string; userId: number; conversationId: string; role: "user" | "assistant"; content: string; model?: string | null }) {
  const db = await workspaceDb();
  await db.insert(davidMessages).values(input);
  await db.update(davidConversations).set({ updatedAt: new Date() }).where(and(eq(davidConversations.userId, input.userId), eq(davidConversations.id, input.conversationId)));
  return input;
}

export async function listDavidRuns(userId: number): Promise<DavidRun[]> {
  const db = await workspaceDb();
  return db.select().from(davidRuns).where(eq(davidRuns.userId, userId)).orderBy(desc(davidRuns.updatedAt)).limit(40);
}

export async function createDavidRun(input: Omit<DavidRun, "createdAt" | "updatedAt">) {
  const db = await workspaceDb();
  await db.insert(davidRuns).values(input);
  return input;
}

export async function updateDavidRun(userId: number, id: string, patch: Partial<Pick<DavidRun, "status" | "plan" | "planData" | "provider">>) {
  const db = await workspaceDb();
  await db.update(davidRuns).set(patch).where(and(eq(davidRuns.userId, userId), eq(davidRuns.id, id)));
}

export async function createDavidRunEvent(input: Omit<DavidRunEvent, "createdAt">) {
  const db = await workspaceDb();
  await db.insert(davidRunEvents).values(input);
  return input;
}

export async function listDavidRunEvents(userId: number, runId: string): Promise<DavidRunEvent[]> {
  const db = await workspaceDb();
  return db.select().from(davidRunEvents).where(and(eq(davidRunEvents.userId, userId), eq(davidRunEvents.runId, runId))).orderBy(davidRunEvents.createdAt);
}
