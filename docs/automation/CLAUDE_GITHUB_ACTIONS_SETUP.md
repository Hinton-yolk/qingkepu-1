# Claude Code GitHub Actions — one-time setup

## Status

The default branch contains `.github/workflows/claude-ep01.yml`. It watches comments on PR #3, but it will not run without a valid Anthropic credential stored as a GitHub Actions secret. This is an opt-in integration; no task will run merely because a file was committed.

## One-time action required from the repository owner

1. In your local Claude Code CLI, run `claude setup-token` to generate a Claude Code OAuth token (supported on eligible Pro/Max plans). Do **not** send the token in a chat, issue or PR comment.
2. In GitHub open `doityj335-prog/kepu-studio` → **Settings → Secrets and variables → Actions → New repository secret**. Use the exact name `CLAUDE_CODE_OAUTH_TOKEN` and paste the token directly into the secret editor.
3. Confirm GitHub Actions is enabled for this private repository and permitted to run `anthropics/claude-code-action@v1` from the repository's Actions settings. If organization policies block the action, allowlist it there; do not weaken other policies.
4. After setup, post a **new** top-level comment on PR #3 beginning with `@claude ` followed by a small task. Older comments will not retroactively trigger a run.
5. Check the new run in the **Actions** tab. If it fails, inspect the job logs. Do not post credential values in any issue/comment.

## Trigger scope and safeguards

- Triggers only on **new comments**, only when the comment author is `doityj335-prog`, only on **PR #3**, and only if the first characters of the body are exactly `@claude `.
- Uses GitHub Actions' built-in `GITHUB_TOKEN`; the official Claude GitHub App is **not necessary for this particular workflow** because `github_token` is supplied explicitly. The Claude Code OAuth token is still required to call Anthropic.
- Uses Sonnet by default, at most 15 Claude turns, and a job timeout of 25 minutes. These are limits on one run, not a guaranteed dollar cap.
- Uses only basic Claude Code GitHub tools by default: commenting, reading/editing/committing files. Executing Blender, Remotion, shell commands, RunPod or uploading Drive media **is not configured** in this initial integration. These require separately scoped tooling/credentials and testing.
- Does not automatically merge PR #3, change Drive sharing or approve paid compute. Keep the existing T4 production/review gates.
- A comment from a GitHub Actions bot typically cannot trigger another Actions workflow using the same built-in token. The intent is GPT-user-initiated tasks, not self-triggering loops.

## First safe smoke test

Use this exact **new** comment on PR #3 after the secret is set:

> @claude Connection test only. Read the latest PR #3 task and reply with a short Chinese summary of the current stage and blockers. Do not modify code, render videos, call paid services, or start T4 production. End your reply with `Claude Actions connected`.

If the test succeeds, GPT can publish a newly authored `@claude` task comment directly on PR #3 to initiate a Claude Code run. For substantial video production, complete a second configuration stage before assuming the hosted runner has Blender/RunPod/Drive access.

## References

- https://github.com/anthropics/claude-code-action/blob/main/docs/usage.md
- https://github.com/anthropics/claude-code-action/blob/main/docs/setup.md
- https://github.com/anthropics/claude-code-action/blob/main/docs/faq.md
