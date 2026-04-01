"""Download and manage YingMusic-SVC model checkpoint."""
import os
from huggingface_hub import hf_hub_download

REPO_ID = "GiantAILab/YingMusic-SVC"
MODEL_FILENAME = "YingMusic-SVC-full.pt"


def get_vendor_path() -> str:
    """Get path to vendor/YingMusic-SVC directory."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(here), "vendor", "YingMusic-SVC")


def get_checkpoint_path() -> str:
    """Download checkpoint if needed and return its path."""
    vendor = get_vendor_path()
    ckpt_dir = os.path.join(vendor, "checkpoints")
    ckpt_path = os.path.join(ckpt_dir, MODEL_FILENAME)

    if os.path.exists(ckpt_path):
        return ckpt_path

    print(f"  Downloading {MODEL_FILENAME} from HuggingFace...")
    os.makedirs(ckpt_dir, exist_ok=True)
    hf_hub_download(
        repo_id=REPO_ID,
        filename=MODEL_FILENAME,
        local_dir=ckpt_dir,
    )
    print(f"  Model saved to {ckpt_path}")
    return ckpt_path


def get_config_path() -> str:
    """Get path to YingMusic-SVC config file."""
    vendor = get_vendor_path()
    return os.path.join(vendor, "configs", "YingMusic-SVC.yml")
