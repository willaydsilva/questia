import hashlib
import hmac
import json
import os
import unicodedata

ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados.json")
ITERACOES = 100_000


# ---------- Utilidades ----------

def normalizar(texto):
    """Ignora maiúsculas, minúsculas e acentos ao comparar textos."""
    texto = texto.strip().lower()
    sem_acento = unicodedata.normalize("NFD", texto)
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")


def gerar_hash_senha(senha):
    """Guarda a senha como 'salt$hash', nunca em texto puro."""
    salt = os.urandom(16)
    hash_ = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, ITERACOES)
    return salt.hex() + "$" + hash_.hex()


def verificar_senha(senha, guardado):
    try:
        salt_hex, hash_hex = guardado.split("$")
        salt = bytes.fromhex(salt_hex)
    except (ValueError, AttributeError):
        return False
    hash_ = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, ITERACOES)
    return hmac.compare_digest(hash_.hex(), hash_hex)


# ---------- Leitura e escrita do JSON ----------

def _proximo_id(dados):
    return max((u.get("id", 0) for u in dados["usuarios"]), default=0) + 1


def _preencher_ids(dados):
    """Dá um id para usuários antigos que ainda não têm. Retorna True se mudou algo."""
    mudou = False
    for usuario in dados["usuarios"]:
        if "id" not in usuario:
            usuario["id"] = _proximo_id(dados)
            mudou = True
    return mudou


def carregar_dados():
    if not os.path.exists(ARQUIVO):
        return {"usuarios": [], "escolas": []}
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        dados = json.load(f)
    dados.setdefault("usuarios", [])
    dados.setdefault("escolas", [])
    if _preencher_ids(dados):
        salvar_dados(dados)
    return dados


def salvar_dados(dados):
    # Grava num arquivo temporário e troca no final, para não corromper o JSON
    temporario = ARQUIVO + ".tmp"
    with open(temporario, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
    os.replace(temporario, ARQUIVO)


# ---------- Usuários (alunos e professores) ----------

def buscar_usuario(nome):
    for usuario in carregar_dados()["usuarios"]:
        if normalizar(usuario["nome"]) == normalizar(nome):
            return usuario
    return None


def buscar_professor(nome):
    usuario = buscar_usuario(nome)
    if usuario and usuario["tipo"] == "professor":
        return usuario
    return None


def adicionar_usuario(usuario):
    """Salva o usuário, gera o id e devolve o usuário completo."""
    dados = carregar_dados()
    usuario["id"] = _proximo_id(dados)
    dados["usuarios"].append(usuario)
    salvar_dados(dados)
    return usuario


def listar_usuarios(tipo=None):
    usuarios = carregar_dados()["usuarios"]
    if tipo is None:
        return usuarios
    return [u for u in usuarios if u["tipo"] == tipo]


def listar_alunos_do_professor(nome_professor):
    return [u for u in listar_usuarios("aluno")
            if normalizar(u.get("professor", "")) == normalizar(nome_professor)]


def atualizar_usuario(id_usuario, novos_dados):
    dados = carregar_dados()
    for usuario in dados["usuarios"]:
        if usuario["id"] == id_usuario:
            usuario.update(novos_dados)
            salvar_dados(dados)
            return True
    return False


def excluir_usuario(id_usuario):
    dados = carregar_dados()
    antes = len(dados["usuarios"])
    dados["usuarios"] = [u for u in dados["usuarios"] if u["id"] != id_usuario]
    if len(dados["usuarios"]) < antes:
        salvar_dados(dados)
        return True
    return False


# ---------- Escolas ----------

def listar_escolas():
    return carregar_dados()["escolas"]


def escola_existe(nome_escola):
    return any(normalizar(e["escola"]) == normalizar(nome_escola)
               for e in listar_escolas())


def adicionar_escola(estado, cidade, escola):
    """Retorna False se a escola já estiver cadastrada."""
    if escola_existe(escola):
        return False
    dados = carregar_dados()
    dados["escolas"].append({"estado": estado, "cidade": cidade, "escola": escola})
    salvar_dados(dados)
    return True