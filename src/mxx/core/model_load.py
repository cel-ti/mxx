
from mxx.core.config import get_profile_path
from mxx.models.ld import LDModel
from mxx.models.maa import MaaModel
from mxx.models.profile import MxxProfile
from mxx.utils.nofuss.toml import load_toml


def get_all_files():
    for file in get_profile_path().glob("*.toml"):
        # Path(file) and name with no extension
        part = str(file.stem).split(".")[-1]   
        yield file, file.stem, None if part == file.stem else part

def get_file(name : str):
    for file, part2, part3 in get_all_files():
        if file.stem == name:
            return file, part2, part3
        
    if "." in name:
        return None
    
    for file, part2, part3 in get_all_files():
        if file.stem.split(".")[0] == name:
            return file, part2, part3
    return None

_cache = {}

def load_model(name : str):
    """
    part is defined as any file that goes like xxx.ld.toml xxx.maa.toml
    """ 
    if name in _cache:
        return _cache[name]

    file_info = get_file(name)
    if file_info is None:
        return None
    file, part2, part3 = file_info
    
    tomldata = load_toml(file)
    for k, v in tomldata.items():
        if isinstance(v, dict) and "template" in v:
            if len(v) != 1:
                raise ValueError(f"Template definition for '{k}' in '{name}' has extra keys.")

            template_name = v["template"]
            template_model = load_model(f"{template_name}.{k}")
            if template_model is None:
                raise ValueError(f"Template model '{template_name}' not found for '{k}' in '{name}'")
            tomldata[k] = template_model

    match part3:
        case "maa":
            data = MaaModel.create(tomldata)
        case "ld":
            data = LDModel.create(tomldata)
        case _:
            data = MxxProfile.create(tomldata)  

    _cache[name] = data
    return data

def get_list():
    for file, part2, part3 in get_all_files():
        yield part2

def get_models():
    for name in get_list():
        model = load_model(name)
        if model is not None:
            yield name, model