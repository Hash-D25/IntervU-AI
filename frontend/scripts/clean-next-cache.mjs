import { rmSync } from "node:fs";
import { resolve } from "node:path";

const cacheDir = resolve(process.cwd(), ".next");

try {
  rmSync(cacheDir, { recursive: true, force: true });
} catch {
  // Ignore if cache is locked; next dev may still recover.
}
