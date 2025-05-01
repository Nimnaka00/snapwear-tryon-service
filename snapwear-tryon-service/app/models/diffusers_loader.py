from diffusers import DiffusionPipeline
import os

def load_pipeline():
    # assume you `git clone levihsu/OOTDiffusion` into project root
    model_dir = "OOTDiffusion"
    # HF token if needed
    token = os.getenv("HF_TOKEN", None)
    pipe = DiffusionPipeline.from_pretrained(model_dir, use_auth_token=token)
    pipe = pipe.to("cuda" if pipe.device.type != "cpu" else "cpu")
    return pipe
