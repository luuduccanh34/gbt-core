from pydantic import BaseModel, Field
from typing import List
class GbtProjectConfig(BaseModel):
    version: str = Field(..., description="The version of the GBT project.")
    name: str = Field(..., description="The name of the GBT project.")
    profiles: str = Field(..., description="The directory where gbt profiles are located.")
    target_path: str = Field(..., description="The directory where gbt target files are located.")
    model_paths: List[str] = Field(..., description="A list of file paths to the model configuration files.")
