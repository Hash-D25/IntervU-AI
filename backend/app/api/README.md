# app/api

HTTP entrypoint aggregation. **One responsibility: compose routers + shared route deps.**

Planned contents:

- `v1/router.py` - mounts every feature router under the versioned prefix.
- `deps.py` - shared route dependencies (auth, pagination, etc.).

Routes validate requests and delegate to services. They never contain business
logic or database queries.
