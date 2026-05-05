# Global Best Practices

## Code Quality
- **SOLID Principles**: Always apply when designing classes/modules.
- **DRY (Don't Repeat Yourself)**: Abstract common logic but avoid premature abstraction.
- **KISS (Keep It Simple, Stupid)**: Prefer readable code over "clever" code.
- **Error Handling**: Never swallow errors. Use specific exceptions and provide context.

## Security
- **Input Validation**: Sanitize all external inputs.
- **Least Privilege**: Only request/use necessary permissions.
- **Secrets**: Never hardcode secrets. Use environment variables.

## Performance
- **Complexity**: Be mindful of O(n) complexity in loops.
- **Caching**: Use caching for expensive operations where appropriate.
- **Lazy Loading**: Load resources only when needed.

## Documentation
- **Self-Documenting Code**: Use clear variable and function names.
- **Comments**: Explain "Why", not "What".
- **Type Hints**: Use TypeScript/Python type hints everywhere.
