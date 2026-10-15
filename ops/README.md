# Operations — a factual first wake, work log and release

These files are **commissioner scaffolding**. They do not mean an agent session is awake, a card is claimed, or any named product has been built. On your real first wake, read your complete private charter and own `agents/NAME/HANDOFF.md`; verify your open card before registering/claiming it. Never copy your private stamped brief into this repository.

## Record real work

From the repository root, use your own exact identity in place of `NAME`:

```sh
python3 ops/field.py event NAME --kind research --stage research \
  --action 'read the model/runtime documentation' \
  --result 'verified version X supports CPU quant inference; citation saved to agents/NAME/research/...' \
  --artifact agents/NAME/research/...
```

Write a new event after each meaningful action, test, discovery, failure/fix, status change or exact handoff. The helper appends to your own `agents/NAME/events.jsonl`, refreshes your one exhaustive `HANDOFF.md`, and updates `status/NAME.json`. Use `working`, `checkpoint`, `blocked`, `failed`, `stopped`, `delivered`, or `not-started` honestly; a fresh timestamp is not evidence that a process or AI session stayed alive. Every active-session update must be factual and no more than five minutes apart. No heartbeat daemon or fake progress.

For a command that should be observed and logged, run it through the tracker. It runs with its working directory set to **your own agent folder**, removes the crew credentials from the child's environment, saves actual combined output under your ignored `agents/NAME/work/` folder, and records the child return code. For this repository's helper checks:

```sh
python3 ops/field.py run NAME --stage helper-tests --push -- \
  python3 -m unittest discover -s ../../tests -v
```

A live PID or successful command is not proof the named product works; inspect output and run product-specific clean-build/acceptance tests too. If the child exits, the record says so. Stop/OS/session shutdown is real; nothing here keeps an AI session privately thinking.

## Publish only your lane

```sh
python3 ops/field.py publish NAME
```

The publisher stages only your `agents/NAME/` and `status/NAME.json`, plus `tests/` only when your charter explicitly assigns it (and `docs/` only for Lookout's public app). It refuses detected foreign staged paths and known live credentials. Never use a blanket `git add -A`, force-push, remove someone else's work, or rewrite history. Rebase/read current `main`, verify the result, and preserve all other sessions' changes. Source pushes are formally recorded by the repository workflow.

## Keep bulky deliverables out of source Git

When a real release is ready, `ops/release.py` accepts explicitly selected source files **inside your own `agents/NAME/` tree**, checks hashes and rejects unsafe/private ZIP content, then publishes immutable versioned release assets and small archive receipts to **dreamer2664/storagecode, the sole primary archive**. A Release upload, screenshot, test script or public source commit by itself is not product acceptance. `ops/archive.py` preserves a deliberately selected closeout. Keep model weights, large binaries, private prompts, live credentials and private stamped briefs out of Git, public messages and every archive. Retired `dreamer2664/storage` is read-only.

Before claiming delivery: run the documented production build and independent end-to-end checks; inspect actual output; preserve all failures and corrections; hash the exact artifact; update your truthful status and HANDOFF; verify the source commit, workflow, release asset and storagecode links remotely. State limitations plainly.
