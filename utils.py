import json
import os
import random
from datetime import datetime

DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"

ELENCO_PADRAO = [
    {"nome": "Carol", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Debora", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Barbara", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Michele", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Duda", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Luzinete", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Cicera", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Dani", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Luciana", "tipo": "Mensalista", "senha": "123"},
    {"nome": "Amanda", "tipo": "Avulsa", "senha": "123"},
    {"nome": "kelly", "tipo": "Avulsa", "senha": "123"}
]

def carregar_dados(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def salvar_dados(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass
