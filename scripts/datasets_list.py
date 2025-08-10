"""
更新hydra的路径配置到api/paths.json
"""

# set working directory, get root path
from omegaconf import DictConfig
import rootutils
ROOT = rootutils.setup_root(__file__, dotenv=True, pythonpath=True, cwd=True)

# import pretty_errors
import hydra

import os
from omegaconf import OmegaConf
import json

@hydra.main(version_base="1.3", config_path="../configs", config_name="api")
def main(cfg: DictConfig) -> None:
    cfg = OmegaConf.to_container(cfg, resolve=True)
    json_path = os.path.join(ROOT, "api", "paths.json")
    with open(json_path, 'w') as f:
        json.dump(cfg, f, indent=4)

if __name__ == "__main__":
    main()
