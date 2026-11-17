
import hashlib
import hmac
import json
import os
import unicodedata

ARQUIVO = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "dados.json"
)

ITERACOES = 100_000


# ---------- Utilidades ----------

def normalizar(texto):
    """Ignora maiúsculas, minúsculas e acentos."""
    texto = texto.strip().lower()
    sem_acento = unicodedata.normalize("NFD", texto)
    return "".join(
        c for c in sem_acento
        if unicodedata.category(c) != "Mn"
    )


def gerar_hash_senha(senha):
    """Armazena a senha como salt$hash."""
    salt = os.urandom(16)
    hash_ = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        ITERACOES
    )
    return salt.hex() + "$" + hash_.hex()


def verificar_senha(senha, guardado):
    try:
        salt_hex, hash_hex = guardado.split("$")
        salt = bytes.fromhex(salt_hex)
    except (ValueError, AttributeError):
        return False

    hash_ = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt,
        ITERACOES
    )

    return hmac.compare_digest(hash_.hex(), hash_hex)


# ---------- Leitura e escrita do JSON ----------

def _proximo_id(dados):
    return max(
        (u.get("id", 0) for u in dados["usuarios"]),
        default=0
    ) + 1


def _preencher_ids(dados):
    """Adiciona IDs aos usuários antigos."""
    mudou = False

    for usuario in dados["usuarios"]:
        if "id" not in usuario:
            usuario["id"] = _proximo_id(dados)
            mudou = True

    return mudou


def carregar_dados():

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            dados = json.load(f)

    except FileNotFoundError:
        return {"usuarios": [], "escolas": []}

    except json.JSONDecodeError as erro:
        raise ValueError("O arquivo JSON está com formato inválido.") from erro

    except UnicodeDecodeError as erro:
        raise ValueError("O arquivo possui problemas de codificação.") from erro

    except PermissionError as erro:
        raise PermissionError("Sem permissão para acessar o arquivo de dados.") from erro

    else:
        if not isinstance(dados, dict):
            raise ValueError("A estrutura principal do JSON precisa ser um dicionário.")

        dados.setdefault("usuarios", [])
        dados.setdefault("escolas", [])

        if not isinstance(dados["usuarios"], list):
            raise ValueError("A lista de usuários está inválida.")

        if not isinstance(dados["escolas"], list):
            raise ValueError("A lista de escolas está inválida.")

        if not all(isinstance(u, dict) for u in dados["usuarios"]):
            raise ValueError("Existem registros de usuários inválidos.")

        if not all(isinstance(e, dict) for e in dados["escolas"]):
            raise ValueError("Existem registros de escolas inválidos.")

        if _preencher_ids(dados):
            salvar_dados(dados)

        return dados

    except OSError as erro:
        raise OSError("Não foi possível acessar o arquivo de dados.") from erro

def salvar_dados(dados):
    """Salva os dados usando um arquivo temporário."""
    temporario = ARQUIVO + ".tmp"

    with open(temporario, "w", encoding="utf-8") as f:
        json.dump(
            dados,
            f,
            ensure_ascii=False,
            indent=4
        )

    os.replace(temporario, ARQUIVO)


# ---------- Usuários: alunos e professores ----------

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
    """Cadastra um usuário e gera seu ID."""
    dados = carregar_dados()

    usuario["id"] = _proximo_id(dados)
    dados["usuarios"].append(usuario)

    salvar_dados(dados)
    return usuario


def listar_usuarios(tipo=None):
    usuarios = carregar_dados()["usuarios"]

    if tipo is None:
        return usuarios

    return [
        u for u in usuarios
        if u["tipo"] == tipo
    ]


def listar_alunos_do_professor(nome_professor):
    return [
        u for u in listar_usuarios("aluno")
        if normalizar(u.get("professor", ""))
        == normalizar(nome_professor)
    ]


def atualizar_usuario(id_usuario, novos_dados):
    dados = carregar_dados()

    for usuario in dados["usuarios"]:
        if usuario["id"] == id_usuario:
            usuario.update(novos_dados)
            salvar_dados(dados)
            return True

    return False


def excluir_usuario(id_usuario):
    """Impede excluir professor com alunos vinculados."""
    dados = carregar_dados()

    for usuario in dados["usuarios"]:
        if usuario["id"] == id_usuario:

            if usuario["tipo"] == "professor":
                alunos = listar_alunos_do_professor(
                    usuario["nome"]
                )

                if alunos:
                    return False

            dados["usuarios"].remove(usuario)
            salvar_dados(dados)
            return True

    return False


# ---------- Escolas ----------

def listar_escolas():
    return carregar_dados()["escolas"]


def escola_existe(nome_escola, cidade, estado):
    """Verifica escola pelo nome, cidade e estado."""
    return any(
        normalizar(e["escola"]) == normalizar(nome_escola)
        and normalizar(e["cidade"]) == normalizar(cidade)
        and normalizar(e["estado"]) == normalizar(estado)
        for e in listar_escolas()
    )


def adicionar_escola(estado, cidade, escola):
    """Evita escolas duplicadas na mesma cidade e estado."""
    if escola_existe(escola, cidade, estado):
        return False

    dados = carregar_dados()

    dados["escolas"].append({
        "estado": estado,
        "cidade": cidade,
        "escola": escola
    })

    salvar_dados(dados)
    return True
