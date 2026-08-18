import { index, int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

export const davidProjects = mysqlTable("david_projects", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: int("userId").notNull(),
  name: varchar("name", { length: 160 }).notNull(),
  description: text("description"),
  status: mysqlEnum("status", ["active", "planning", "complete", "archived"]).default("active").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
}, (table) => [index("david_projects_user_idx").on(table.userId)]);

export const davidTasks = mysqlTable("david_tasks", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: int("userId").notNull(),
  projectId: varchar("projectId", { length: 36 }),
  title: varchar("title", { length: 240 }).notNull(),
  description: text("description"),
  status: mysqlEnum("status", ["todo", "in_progress", "blocked", "done"]).default("todo").notNull(),
  priority: mysqlEnum("priority", ["low", "normal", "high"]).default("normal").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
}, (table) => [index("david_tasks_user_idx").on(table.userId), index("david_tasks_project_idx").on(table.projectId)]);

export const davidMemories = mysqlTable("david_memories", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: int("userId").notNull(),
  kind: mysqlEnum("kind", ["fact", "preference", "decision", "learning", "note"]).default("note").notNull(),
  content: text("content").notNull(),
  source: varchar("source", { length: 160 }).default("owner"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
}, (table) => [index("david_memories_user_idx").on(table.userId)]);

export const davidConversations = mysqlTable("david_conversations", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: int("userId").notNull(),
  title: varchar("title", { length: 160 }).notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
}, (table) => [index("david_conversations_user_idx").on(table.userId)]);

export const davidMessages = mysqlTable("david_messages", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: int("userId").notNull(),
  conversationId: varchar("conversationId", { length: 36 }).notNull(),
  role: mysqlEnum("role", ["user", "assistant"]).notNull(),
  content: text("content").notNull(),
  model: varchar("model", { length: 96 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
}, (table) => [index("david_messages_conversation_idx").on(table.conversationId), index("david_messages_user_idx").on(table.userId)]);

export const davidRuns = mysqlTable("david_runs", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: int("userId").notNull(),
  conversationId: varchar("conversationId", { length: 36 }),
  objective: text("objective").notNull(),
  plan: text("plan"),
  planData: text("planData"),
  status: mysqlEnum("status", ["queued", "planning", "waiting_approval", "executing", "complete", "degraded", "failed"]).default("queued").notNull(),
  provider: varchar("provider", { length: 96 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
}, (table) => [index("david_runs_user_idx").on(table.userId), index("david_runs_conversation_idx").on(table.conversationId)]);

export const davidRunEvents = mysqlTable("david_run_events", {
  id: varchar("id", { length: 36 }).primaryKey(),
  userId: int("userId").notNull(),
  runId: varchar("runId", { length: 36 }).notNull(),
  type: mysqlEnum("type", ["goal_received", "plan_created", "model_selected", "response_streaming", "verification_started", "verification_passed", "run_degraded", "run_failed"]).notNull(),
  state: mysqlEnum("state", ["planning", "thinking", "executing", "verifying", "complete", "degraded", "failed"]).notNull(),
  actor: varchar("actor", { length: 96 }).default("David AI").notNull(),
  summary: varchar("summary", { length: 500 }).notNull(),
  provider: varchar("provider", { length: 96 }),
  metadata: text("metadata"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
}, (table) => [index("david_run_events_run_idx").on(table.runId), index("david_run_events_user_idx").on(table.userId)]);

export type DavidProject = typeof davidProjects.$inferSelect;
export type DavidTask = typeof davidTasks.$inferSelect;
export type DavidMemory = typeof davidMemories.$inferSelect;
export type DavidConversation = typeof davidConversations.$inferSelect;
export type DavidMessage = typeof davidMessages.$inferSelect;
export type DavidRun = typeof davidRuns.$inferSelect;
export type DavidRunEvent = typeof davidRunEvents.$inferSelect;
