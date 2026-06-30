# infoPipeline

## Run the tests

```bash
python3 -m unittest discover -s tests -t .
```

## Run the application

Run the default configured profile once:

```bash
python3 planner.py
```

Run a specific configured profile:

```bash
python3 planner.py --profile techno-releases
```

Validate the default configuration without running the pipeline:

```bash
python3 planner.py --validate-config
```

Validate a specific profile without running the pipeline:

```bash
python3 planner.py --validate-config --profile techno-releases
```

Configuration validation checks that the selected profile can be loaded and
assembled. It does not call providers, write a ledger, or send Telegram
messages, so it is the safest first check after editing `config/pipeline.yaml`,
prompt paths, templates, profiles, providers, or delivery configuration.

Show the application version:

```bash
python3 planner.py --version
```

`--version` exits before any pipeline or validation work runs.

## Configuration

The default pipeline is assembled from `config/pipeline.yaml`. Topic selection
happens through profiles: each profile supplies the Researcher prompt, Curator
prompt, Writer prompt, and Writer template paths. Prompt filenames may be
topic-specific. To retarget the pipeline, select a different profile or add one
that points at different prompt files rather than changing Python source code.
