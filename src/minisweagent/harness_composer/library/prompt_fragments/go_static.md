## Go Policy

- Use package-level search and inspect the closest `_test.go` files.
- Prefer `go test ./path/to/package` before `go test ./...` when the failure scope is clear.
- Check exported API changes against nearby tests and callers.
