# Changelog

All notable changes to this project will be documented in this file.

Please choose versions by [Semantic Versioning](http://semver.org/).

* MAJOR version when you make incompatible API changes,
* MINOR version when you add functionality in a backwards-compatible manner, and
* PATCH version when you make backwards-compatible bug fixes.

## v0.1.0

- Initial release with MCP server for Alertmanager integration
- Add 4 tools: list_alerts, get_alert, silence_alert, unsilence_alert
- Migrate to src/ layout with strict mypy configuration
- Add comprehensive logging and error handling
- Add Makefile with sync, format, lint, typecheck, check, test, precommit targets
- Add comprehensive test suite
