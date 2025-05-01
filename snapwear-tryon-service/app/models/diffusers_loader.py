from diffusers import DiffusionPipeline
import torch
import os

_pipe: DiffusionPipeline = None

def get_pipeline():
    global _pipe
    if _pipe is None:
        # point this to the local clone or the HF repo
        model_path = os.getenv("OOTDIFFUSION_PATH", "OOTDiffusion")
        _pipe = DiffusionPipeline.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            safety_checker=None,
        )
        _pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    return _pipe
