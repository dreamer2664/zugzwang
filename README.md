# Zugzwang — a real UCI chess engine and a fair, recorded challenge

Build an original local chess-playing engine, not an API wrapper. Legal move/rule correctness, a standard UCI CLI, substantive search/evaluation, reproducible self-play, independent verification and immutable PGNs all matter.

The desired **testable finite claim**: 100% drawn against the identical verified binary/config on a preregistered self-play tournament; 100% won by the stronger build against a truly only-slightly-weaker same-family clone on a separate locked challenge. Retain every game. No opponent-ID special cases, forced results, selected-afterward opening suite, clock tampering or discarded loss. Chess is unsolved: a finite tournament cannot prove a universal theorem for every legal game, position or opponent. Never state it does; report honest exact results if strict targets aren't met.

Read [the complete ZUGZWANG brief](briefs/ZUGZWANG.md), own handoff and [project scope](docs/PROJECT_SCOPE.md). Initial status is setup/not started, zero game results/ratings, no chess engine.

Source in `agents/zugzwang/`. Locally built source/binary/tournament evidence archives to sole primary storagecode `data/zugzwang/zugzwang/...`, versioned tags `zugzwang/zugzwang/rNN-<hash>`. UCI protocol/licensing, paired color/time settings and suite hashes must accompany any strength claim.
