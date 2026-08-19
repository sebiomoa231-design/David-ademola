import { afterEach, describe, expect, it, vi } from "vitest";
import { api, toAudioUrl } from "./api";

const canonicalBase = "https://david-ademola.onrender.com";

describe("Command Center API contracts", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("formats a real returned audio payload without substituting a browser voice", () => {
    expect(toAudioUrl("YXVkaW8=", "mp3")).toBe("data:audio/mp3;base64,YXVkaW8=");
  });

  it("uses the deployed root health route only when the canonical API health route is unavailable", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response("Not found", { status: 404, statusText: "Not Found" }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ status: "ok", service: "David AI backend" }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(api.health()).resolves.toEqual({ status: "ok", service: "David AI backend" });
    expect(fetchMock).toHaveBeenNthCalledWith(1, `${canonicalBase}/api/health`, expect.objectContaining({ cache: "no-store" }));
    expect(fetchMock).toHaveBeenNthCalledWith(2, `${canonicalBase}/health`, expect.objectContaining({ cache: "no-store" }));
  });

  it("sends Voice workspace requests to the existing synthesis endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ audio_available: false, provider: "configured", text_fallback: "Audio unavailable" }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    const response = await api.synthesize("David, report status");

    expect(response.audio_available).toBe(false);
    expect(fetchMock).toHaveBeenCalledWith(`${canonicalBase}/api/voice/synthesize`, expect.objectContaining({ method: "POST", body: JSON.stringify({ text: "David, report status", language_mode: "AUTO" }) }));
  });

  it("links a Website Builder request to the selected shared project without fabricating a preview", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ title: "Blueprint", sections: [], notes: [], generation_id: "generation-1" }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    const response = await api.websiteGenerate("Build a client portal", "project-7");

    expect(response.generation_id).toBe("generation-1");
    expect(fetchMock).toHaveBeenCalledWith(`${canonicalBase}/api/website/generate`, expect.objectContaining({ method: "POST", body: JSON.stringify({ prompt: "Build a client portal", project_id: "project-7" }) }));
  });

  it("loads Automation workspace records only from the registered backend workflow contract", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ workflows: [{ id: "briefing", name: "Daily briefing" }] }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    const response = await api.intelligence.workflows();

    expect(response).toEqual({ workflows: [{ id: "briefing", name: "Daily briefing" }] });
    expect(fetchMock).toHaveBeenCalledWith(`${canonicalBase}/api/intelligence/workflows`, expect.objectContaining({ cache: "no-store" }));
  });

  it("uses the canonical goal, plan, run, authorization, and execution endpoints in explicit order", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ id: "goal-1", objective: "Prepare a governed research brief" }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ id: "plan-1", goal_id: "goal-1" }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ id: "run-1", goal_id: "goal-1", status: "planned" }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ run_id: "run-1", authorized: true }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ run_id: "run-1", status: "running" }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    const goal = await api.intelligence.createGoal("Prepare a governed research brief", { interface: "command-center" });
    await api.intelligence.planGoal(goal.id);
    const run = await api.intelligence.createRun(goal.id, goal.objective, "research");
    await api.intelligence.authorizeRun(run.id, "research");
    await api.intelligence.executeRun(run.id, { approved: true, objective: goal.objective, requested_capability: "research", input: { authorization: "explicit-user-action" } });

    expect(fetchMock).toHaveBeenNthCalledWith(1, `${canonicalBase}/api/intelligence/goals`, expect.objectContaining({ method: "POST", body: JSON.stringify({ title: "Prepare a governed research brief", objective: "Prepare a governed research brief", context: { interface: "command-center" } }) }));
    expect(fetchMock).toHaveBeenNthCalledWith(2, `${canonicalBase}/api/intelligence/goals/goal-1/plan`, expect.objectContaining({ method: "POST" }));
    expect(fetchMock).toHaveBeenNthCalledWith(3, `${canonicalBase}/api/intelligence/runs`, expect.objectContaining({ method: "POST", body: JSON.stringify({ goal_id: "goal-1", objective: "Prepare a governed research brief", requested_capability: "research" }) }));
    expect(fetchMock).toHaveBeenNthCalledWith(4, `${canonicalBase}/api/intelligence/runs/run-1/authorize?capability=research`, expect.objectContaining({ method: "POST" }));
    expect(fetchMock).toHaveBeenNthCalledWith(5, `${canonicalBase}/api/intelligence/runs/run-1/execute`, expect.objectContaining({ method: "POST", body: JSON.stringify({ approved: true, objective: "Prepare a governed research brief", requested_capability: "research", input: { authorization: "explicit-user-action" } }) }));
  });

  it("surfaces backend failures instead of inventing a content planning result", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("Content planner unavailable", { status: 503, statusText: "Unavailable" })));

    await expect(api.planCreate("Create a launch brief")).rejects.toThrow("Content planner unavailable");
  });
});
