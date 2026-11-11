import json
import os
import unicodedata

ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados.json")


def carregar_dados():
    if not os.path.exists(ARQUIVO):
        return {"usuarios": [], "escolas": []}
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_dados(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def normalizar(texto):
    texto = texto.strip().lower()
    sem_acento = unicodedata.normalize("NFD", texto)
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")


def buscar_usuario(nome):
    dados = carregar_dados()
    for usuario in dados["usuarios"]:
        if normalizar(usuario["nome"]) == normalizar(nome):
            return usuario
    return None


def adicionar_usuario(usuario):
    dados = carregar_dados()
    dados["usuarios"].append(usuario)
    salvar_dados(dados)


def adicionar_escola(estado, cidade, escola):
    dados = carregar_dados()
    dados["escolas"].append({"estado": estado, "cidade": cidade, "escola": escola})
    salvar_dados(dados)


def listar_usuarios(tipo=None):
    dados = carregar_dados()
    if tipo is None:
        return dados["usuarios"]
    return [u for u in dados["usuarios"] if u["tipo"] == tipo]


def atualizar_usuario(nome, novos_dados):
    dados = carregar_dados()
    for usuario in dados["usuarios"]:
        if normalizar(usuario["nome"]) == normalizar(nome):
            usuario.update(novos_dados)
            salvar_dados(dados)
            return True
    return False


def excluir_usuario(nome):
    dados = carregar_dados()
    antes = len(dados["usuarios"])
    dados["usuarios"] = [u for u in dados["usuarios"]
                         if normalizar(u["nome"]) != normalizar(nome)]
    if len(dados["usuarios"]) < antes:
        salvar_dados(dados)
        return True
    return False