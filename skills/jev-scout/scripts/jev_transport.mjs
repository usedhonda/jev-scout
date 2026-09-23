#!/usr/bin/env node

import { fileURLToPath } from "node:url";
import path from "node:path";

const API_URL = "https://api.typesafe.ai/v1/systemone";
const MAX_SUCCESS_BYTES = 1024 * 1024;
const MAX_ERROR_BYTES = 4096;

async function readBounded(response, limit, rejectOversize) {
  const reader = response.body?.getReader();
  if (!reader) {
    const bytes = Buffer.from(await response.arrayBuffer());
    if (rejectOversize && bytes.length > limit) throw new Error("response too large");
    return bytes.subarray(0, limit + 1);
  }
  const chunks = [];
  let total = 0;
  try {
    while (total <= limit) {
      const { value, done } = await reader.read();
      if (done) break;
      const chunk = Buffer.from(value);
      const remaining = limit + 1 - total;
      chunks.push(chunk.subarray(0, remaining));
      total += chunk.length;
      if (total > limit && rejectOversize) throw new Error("response too large");
    }
  } finally {
    if (total > limit) await reader.cancel().catch(() => {});
  }
  return Buffer.concat(chunks).subarray(0, limit + 1);
}

export async function transport(input, fetchImpl = globalThis.fetch) {
  const body = Buffer.from(input.body, "base64");
  const response = await fetchImpl(API_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${input.key}`,
      "Content-Type": "application/json",
    },
    body,
    redirect: "error",
    signal: AbortSignal.timeout(input.timeout_ms),
  });
  const limit = response.status >= 200 && response.status < 300
    ? MAX_SUCCESS_BYTES : MAX_ERROR_BYTES;
  const bytes = await readBounded(response, limit, response.status >= 200 && response.status < 300);
  return { status: response.status, body: Buffer.from(bytes).toString("base64") };
}

async function main() {
  const input = JSON.parse(await readStdin());
  const result = await transport(input);
  process.stdout.write(JSON.stringify(result));
}

function readStdin() {
  return new Promise((resolve, reject) => {
    const chunks = [];
    process.stdin.on("data", (chunk) => chunks.push(chunk));
    process.stdin.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    process.stdin.on("error", reject);
  });
}

const invokedPath = process.argv[1] ? path.resolve(process.argv[1]) : null;
if (invokedPath && fileURLToPath(import.meta.url) === invokedPath) {
  main().catch(() => process.exitCode = 1);
}
