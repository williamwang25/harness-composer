## Python Pytest Policy

- Search for the failing symbol, test name, or error text before opening broad files.
- Prefer targeted `pytest path::test_name -q` runs when a likely test is known.
- Use `pytest -q` as the default broad verification command only after targeted checks.
- Treat traceback frames, assertion diffs, and the short test summary as the highest-value output.
