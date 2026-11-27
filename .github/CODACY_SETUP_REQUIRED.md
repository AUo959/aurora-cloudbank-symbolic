# Codacy integration status

The disabled Actions workflows `codacy.yml` and `codacy-analysis.yml` were retired
on November 9, 2026. They executed no analysis. Do not dispatch these filenames.

Codacy Static Code Analysis is an external GitHub App integration. Diagnose its
checks in the Codacy dashboard and the app installation settings. Its repository
configuration remains in place. No app settings or secrets were changed by the
CI consolidation. Canonical Python validation is the Actions **CI Check** job;
CodeQL remains a separate security workflow.

If the external app reports “Project Configuration not found”, check that the
repository is registered in the Codacy dashboard and that its integration points
to this repository. Retiring the disabled workflows does not repair app setup.
