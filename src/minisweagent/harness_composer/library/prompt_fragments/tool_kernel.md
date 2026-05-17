## Available Harness Modules

Use the enabled modules through ordinary shell commands:

- search_code: use `rg -n` with focused patterns and path filters.
- view_file: use line-numbered, range-based views such as `nl -ba path | sed -n 'start,endp'`.
- safe_edit: make minimal edits and inspect the changed range immediately afterward.
- run_test: run the smallest relevant test first, then broaden only when needed.
- summarize_obs: when output is long, redirect it to a file and inspect the failing/error blocks.
- state: keep short local notes for long investigations when the policy enables external state.
