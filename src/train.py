# set working directory, get root path
from omegaconf import DictConfig
import rootutils
ROOT = rootutils.setup_root(__file__, dotenv=True, pythonpath=True, cwd=True)

# import pretty_errors
from rich import print

import hydra
from omegaconf import OmegaConf

import ultralytics
from ultralytics import YOLO, RTDETR

def oc_to_dict(omf: DictConfig) -> dict:
    return OmegaConf.to_container(omf, resolve=True) # type: ignore

@hydra.main(version_base="1.3", config_path="../configs", config_name="config")
def main(cfg: DictConfig) -> None:
    
    ultralytics.settings["datasets_dir"] = cfg.paths.data_dir
    ultralytics.settings["wandb"] = cfg.use_wandb
    
    model_dict = oc_to_dict(cfg.model)
    if model_dict.get("name", None) is None:
        model_dict["name"] = "Test"
    else:
        cfg.logger.tags = model_dict["name"].split("-")
    print(model_dict["name"])
    try :
        if "yolo" in model_dict["name"]:
            model = YOLO(model_dict)
        elif "rtdetr" in model_dict["name"]:
            model = RTDETR(model_dict) # type: ignore
    except Exception as e:
        print(f"初始化模型错误: {e}")
        return

    model.train(
        project=f"{cfg.paths.output_dir}/{cfg.project_name}",
        name=cfg.run_name,
        data=cfg.data.file, 
        cfg=oc_to_dict(cfg.setting),
        epochs=cfg.epochs,
        device=cfg.device,
        batch=cfg.batch,
        # fraction=0.1,
        # patience=0,
        # amp=False,
        logger=oc_to_dict(cfg.logger),
        data_layout=cfg.data_layout,    
    )

if __name__ == "__main__":
    main()
