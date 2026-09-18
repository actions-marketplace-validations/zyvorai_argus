# Copyright 2026 Zyvor AI Labs · https://zyvor.dev
# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-Argus-Commercial
"""Test intelligence: flake classification, quarantine, change-based
selection, and a failure-studio payload. File-backed on purpose — no new
store schema, so SQLite and Postgres stay on the same public surface.
"""
