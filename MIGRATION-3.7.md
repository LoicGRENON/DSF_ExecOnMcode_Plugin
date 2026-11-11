# DWC / DSF 3.7 migration

This branch targets DuetWebControl 3.7.0 and DuetSoftwareFramework 3.7.0.
The DWC frontend requires Vue 3, Vuetify 4, Pinia and the Vite plugin loader.
The backend supports both dsf-python 3.6 (IPC 12) and 3.7 (IPC 13), because a
DSF 3.7 installation can still carry the older Python package.

## Changes

- Port route registration and the settings UI to the DWC 3.7 plugin API.
- Read/write configuration through standard DWC download/upload actions,
  replacing the custom HTTP listener. Opening the panel only reads the file.
- After a successful save, send the existing `M1200` filter-reload code.
  Configured commands are not executed by the editor.
- Handle both `resolve_path()` return forms, enum naming conventions and
  `majorNumber` / `major_number` without changing the installed Python package.
- Preserve the configuration path and custom fields. Editing uses a copy so
  cancelling an edit cannot mutate the live table.
- Validate duplicate/reserved M-codes and allocate free codes from unsorted lists.
- Enforce LF line endings for executable Python scripts on Windows checkouts.
- Update the packaging workflow to the DWC 3.7 build script.

The custom HTTP endpoint implementation is removed; configuration clients should
use the standard DSF/DWC file APIs for `0:/sys/ExecOnMcode/ExecOnMcode.json` and
reload filters with `M1200` after saving. The configuration file is not part of
the installation payload, so upgrades preserve existing commands.

## Build and test

With DWC 3.7.0 checked out at `/path/to/DuetWebControl` and its npm dependencies
installed, run from this repository:

```sh
npm test
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
node /path/to/DuetWebControl/scripts/build-plugin-pkg.js src
```

Node.js 22.18+ or 24 LTS is recommended; the Python tests support Python 3.11+.
The ZIP is written to `src/ExecOnMcode-<version>.zip`. Both DWC source type checking
and Vite bundling are performed by the build script. CI runs the backend tests
against pinned revisions of the official dsf-python 3.6 and 3.7 clients.

Tests cover configuration loading/defaults, preservation of extra fields,
validation, save/reload ordering, upload/reload failures, compatibility adapters,
and interception with subprocess execution mocked out.

## Hardware validation and limits

The rc.5 migration was installed on a DSF/DWC 3.7.0 system with dsf-python 3.6.0.
This rc.6 proposal additionally extracts the configuration transport for isolated
testing and removes the unused custom HTTP implementation; those final changes
were checked locally and have not been reinstalled on the live system.
The backend remained running, the frontend displayed the existing configuration,
and the configuration bytes were unchanged after installation. No configured
command or G-code was executed, and no save/delete operation was performed on the
live configuration. End-to-end live save/reload and actual command execution
therefore remain for maintainer validation. No firmware or system packages were
updated during this validation.
