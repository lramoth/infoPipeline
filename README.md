# infoPipeline

## Run the tests

```bash
python3 -m unittest discover -s tests -t .
```

## Run the application

```bash
python3 planner.py
```

Run a specific configured profile:

```bash
python3 planner.py --profile techno
```

## Configuration

The default pipeline is assembled from `config/pipeline.yaml`. Topic selection
happens through profiles: each profile supplies the Researcher prompt, Curator
prompt, Writer prompt, and Writer template paths. Prompt filenames may be
topic-specific. To retarget the pipeline, select a different profile or add one
that points at different prompt files rather than changing Python source code.
