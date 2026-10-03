/**
 * Adversarial (Tier 5) runner.
 *
 * Executes the two white-box stress harnesses written by the challenger agents
 * during the 2026-09-26 platform build and prints every recorded result.
 *
 * Exit code 0 = no CRITICAL/HIGH defect recorded, 1 = at least one.
 * Executable via: `npm run test:adversarial`
 */

import { sarAdversarialHarness } from "./sar_stress.harness";
import { AdversarialHarnessChallenger2 } from "./m1_dossier_stress.harness";

async function main(): Promise<void> {
  console.log("== SAR / M2 / commercial tasking stress harness");
  const sarResults = sarAdversarialHarness.runAll();
  for (const r of sarResults) {
    const tag = r.passed ? "PASS" : "FAIL";
    const defect = r.defectIdentified ? " [DEFECT NOTED]" : "";
    console.log(`  [${tag}] ${r.testId} ${r.name}${defect}`);
    if (r.defectIdentified && r.notes) console.log(`         ${r.notes}`);
  }
  const sarFailures = sarResults.filter((r) => !r.passed).length;

  console.log("\n== M1 geometry / MCR 2-9 dossier stress harness");
  const m1 = new AdversarialHarnessChallenger2();
  const summary = await m1.runAll();
  for (const r of m1.results) {
    const tag = r.passed ? "PASS" : `FAIL:${r.severity}`;
    console.log(`  [${tag}] ${r.id} ${r.name}`);
  }

  console.log(
    `\nSAR harness: ${sarResults.length - sarFailures}/${sarResults.length} passed` +
      ` (${sarResults.filter((r) => r.defectIdentified).length} known defects noted)`
  );
  console.log(
    `M1/dossier harness: ${summary.passed}/${summary.total} passed, ` +
      `${summary.criticalDefects} critical/high defects -> ${summary.verdict}`
  );

  process.exit(sarFailures > 0 || summary.criticalDefects > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
