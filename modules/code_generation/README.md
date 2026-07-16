# Code Generation

This feature module owns Aurora's specification-driven Python code generator.
It produces functions, classes, tests, documentation, and generation audit
metadata from explicit specifications.

New consumers should import from `modules.code_generation`. The legacy
`src.code_generation_framework` path remains a compatibility import; removal
would require separate approval.
