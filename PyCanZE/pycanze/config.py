from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None  # type: ignore


def load_config(path: Optional[Path], overrides: Dict[str, Any]) -> Dict[str, Any]:
    """Load a YAML/JSON config file and merge CLI overrides.

    Parameters
    ----------
    path:
        Optional path to a configuration file. When ``None`` no file is read.
    overrides:
        Mapping of CLI-provided values which should take precedence over the
        file contents. Entries with ``None`` values are ignored.
    """

    cfg: Dict[str, Any] = {}
    if path:
        text = path.read_text()
        if path.suffix.lower() in {".yaml", ".yml"}:
            if yaml is None:  # pragma: no cover - import guard
                raise RuntimeError("pyyaml is required for YAML configuration files")
            cfg = yaml.safe_load(text) or {}
        else:
            cfg = json.loads(text)
        # Resolve relative log paths against the config location
        for key in ("log_csv", "log_sqlite"):
            if key in cfg and cfg[key] is not None:
                p = Path(cfg[key])
                if not p.is_absolute():
                    p = path.parent / p
                cfg[key] = p
    for k, v in overrides.items():
        if v is not None:
            cfg[k] = v
    return cfg
