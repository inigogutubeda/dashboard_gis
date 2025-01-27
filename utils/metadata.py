# utils/metadata.py
import json
import os

def load_datasets_metadata(json_path="datasets_metadata.json"):
    """
    Carga el archivo JSON con la información (unidades, descripción) de cada dataset.
    Retorna un diccionario con la estructura { dataset_name: { units: ..., description: ... } }
    """
    if not os.path.exists(json_path):
        # En caso de que no exista, devolvemos un dict vacío o lanzamos error
        return {}

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
