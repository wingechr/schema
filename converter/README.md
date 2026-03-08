# README

there should be a conversion function, so we can automatically create an update chain

## Examples

```bash
python -m converter METADATA_PATH.json NEW_SCHEMA_VERSION
```

```python
from convert import MetadataConverterGraph

MetadataConverterGraph().convert(
    {"$schema": "https://purl.org/dat/schema/schema-v0.json"},
    "https://purl.org/dat/schema/schema-v1.json"
)
```
