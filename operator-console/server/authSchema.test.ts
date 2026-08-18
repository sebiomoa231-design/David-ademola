import { describe, expect, it } from "vitest";
import { users } from "../drizzle/schema";
import { getDb } from "./db";

describe("secure user persistence schema", () => {
  it("provides the users table required by the OAuth callback", async () => {
    const db = await getDb();
    expect(db).not.toBeNull();

    await expect(db!.select({ id: users.id }).from(users).limit(1)).resolves.toBeInstanceOf(Array);
  });
});
