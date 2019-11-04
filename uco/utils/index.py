from pathlib import Path

import torch
import pandas as pd
from tqdm import tqdm


class Indexer:

    fields = [
        "mean_dice",
        "encoder",
        "decoder",
        "dropout",
        "augs",
        "img_height",
        "img_width",
        "batch_size",
        "bce_weight",
        "dice_weight",
        "smooth",
        "encoder_lr",
        "decoder_lr",
        "seed",
    ]

    checkpoint_partial_path = "checkpoints/model_best.pth"
    index_filename = "index.csv"

    @classmethod
    def reindex(cls, path):
        path = Path(path)

        items = []
        for child in tqdm(path.iterdir()):
            if not child.is_dir():
                continue
            try:
                items.append(cls.extract_config(child))
            except Exception as ex:
                print(f"{child}: {ex}")
        df = pd.DataFrame.from_records(items)
        save_as = path / cls.index_filename
        df.to_csv(save_as, index=False)

    @classmethod
    def index(cls, run):
        config = cls.extract_config(run)
        parent = run.parent
        index_filename = parent / cls.index_filename
        try:
            df = pd.read_csv(index_filename)
            df.append(config, ignore_index=True)
        except FileNotFoundError:
            df = pd.DataFrame.from_records([config])
        df.to_csv(index_filename, index=False)

    @classmethod
    def extract_config(cls, run_dir):
        checkpoint = torch.load(
            run_dir / cls.checkpoint_partial_path, map_location=torch.device("cpu")
        )

        best_score = checkpoint["monitor_best"].item()
        train_cfg = checkpoint["config"]

        settings = {
            "mean_dice": best_score,
            "run": run_dir.name,
            "encoder": train_cfg["arch"]["args"]["encoder_name"],
            "decoder": train_cfg["arch"]["type"],
            "dropout": train_cfg["arch"]["args"]["dropout"],
            "augs": train_cfg["augmentation"]["type"],
            "img_height": train_cfg["augmentation"]["args"]["height"],
            "img_width": train_cfg["augmentation"]["args"]["width"],
            "batch_size": train_cfg["data_loader"]["args"]["batch_size"],
            "bce_weight": train_cfg["loss"]["args"]["bce_weight"],
            "dice_weight": train_cfg["loss"]["args"]["dice_weight"],
            "encoder_lr": train_cfg["optimizer"]["encoder"]["lr"],
            "decoder_lr": train_cfg["optimizer"]["decoder"]["lr"],
            "seed": train_cfg["seed"],
        }

        return settings
