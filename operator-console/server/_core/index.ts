import "dotenv/config";
import express from "express";
import { createServer } from "http";
import net from "net";
import { createExpressMiddleware } from "@trpc/server/adapters/express";
import { registerOAuthRoutes } from "./oauth";
import { registerStorageProxy } from "./storageProxy";
import { appRouter } from "../routers";
import { createContext } from "./context";
import { serveStatic, setupVite } from "./vite";
import { streamAsDavid } from "../davidAgent";
import { sdk } from "./sdk";

function isPortAvailable(port: number): Promise<boolean> {
  return new Promise(resolve => {
    const server = net.createServer();
    server.listen(port, () => {
      server.close(() => resolve(true));
    });
    server.on("error", () => resolve(false));
  });
}

async function findAvailablePort(startPort: number = 3000): Promise<number> {
  for (let port = startPort; port < startPort + 20; port++) {
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error(`No available port found starting from ${startPort}`);
}

async function startServer() {
  const app = express();
  const server = createServer(app);
  // Configure body parser with larger size limit for file uploads
  app.use(express.json({ limit: "50mb" }));
  app.use(express.urlencoded({ limit: "50mb", extended: true }));
  registerStorageProxy(app);
  registerOAuthRoutes(app);
  app.post("/api/david/chat-stream", async (req, res) => {
    const user = await sdk.authenticateRequest(req).catch(() => null);
    if (!user) {
      res.status(401).json({ error: "Please login before starting a David AI conversation." });
      return;
    }
    const message = typeof req.body?.message === "string" ? req.body.message.trim() : "";
    const conversationId = typeof req.body?.conversationId === "string" ? req.body.conversationId : undefined;
    const rawMemoryIds: unknown[] = Array.isArray(req.body?.memoryIds) ? req.body.memoryIds as unknown[] : [];
    const memoryIds = rawMemoryIds.filter((id): id is string => typeof id === "string").slice(0, 12);
    if (!message || message.length > 4000) {
      res.status(400).json({ error: "A message between 1 and 4000 characters is required." });
      return;
    }
    let closed = false;
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache, no-transform");
    res.setHeader("Connection", "keep-alive");
    res.flushHeaders();
    res.on("close", () => { closed = true; });
    const emit = (event: string, payload: unknown) => { if (!closed) res.write(`event: ${event}\ndata: ${JSON.stringify(payload)}\n\n`); };
    try {
      const result = await streamAsDavid({ userId: user.id, message, conversationId, memoryIds, onToken: (token) => emit("token", { token }), onEvent: (event) => emit("run_event", event) });
      emit("complete", { conversationId: result.conversationId, runId: result.runId, model: result.model });
    } catch (error) {
      emit("error", { message: error instanceof Error ? error.message : "David could not complete this response." });
    } finally {
      if (!closed) res.end();
    }
  });
  // tRPC API
  app.use(
    "/api/trpc",
    createExpressMiddleware({
      router: appRouter,
      createContext,
    })
  );
  // development mode uses Vite, production mode uses static files
  if (process.env.NODE_ENV === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  const preferredPort = parseInt(process.env.PORT || "3000");
  const port = await findAvailablePort(preferredPort);

  if (port !== preferredPort) {
    console.log(`Port ${preferredPort} is busy, using port ${port} instead`);
  }

  server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
  });
}

startServer().catch(console.error);
