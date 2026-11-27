# Changelog

All notable changes to Snowflake Query Optimizer are documented in this file.

## [1.0.0] - 2026-11-27

### Added
- Interactive chatbot for database optimization queries
- Comprehensive Snowflake database analysis (queries, schema, costs, workloads)
- Docker containerization for cross-platform deployment
- Security guide for credential management and production deployment
- Multiple analysis commands: analyze, chat, cost-report, query-insights, schema-check, workload-analysis

### Fixed
- SQL compatibility with standard Snowflake account_usage views
- QueryInsight object attribute access in chat context
- Division by zero errors in cost calculations
- Python DLL restrictions on Windows AppStore version

### Documentation
- Production deployment guide (SECURITY.md)
- Release checklist (RELEASE_CHECKLIST.md)
- Docker setup instructions (DOCKER_SETUP.md)
- Comprehensive README with examples

### Technical Details
- Removed non-standard Snowflake columns: COMPUTE_PROVISIONED_TIME, QUEUE_TIME, COMPILATION_TIME, CREDITS_USED (query_history)
- Mapped BYTES_SCANNED to ROWS_SCANNED for analyzer compatibility
- Switched clustering queries to information_schema for compatibility
- Enhanced chatbot to provide SQL solutions with impact metrics

## Release Status
✅ Production-ready - All core features tested and documented
