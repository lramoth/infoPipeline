# infoPipeline

## Run the tests

```bash
python3 -m unittest discover -s tests -t .
```

## Run the application

```bash
python3 planner.py
```

## Configuration

The default pipeline is assembled from `config/pipeline.yaml`. Topic selection
currently happens through the configured Researcher and Curator prompt files, so
prompt filenames may be topic-specific. To retarget the pipeline, point the
configured prompt paths at different prompt files rather than changing Python
source code.
