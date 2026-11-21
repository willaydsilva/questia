import json
import os
import shutil
import sys
import unicodedata
from datetime import datetime

# =====================================================================
# 0. EXCEÇÕES PERSONALIZADAS
# =====================================================================

class QuestiAIError(Exception):
    """Classe base: todos os erros do programa herdam dela."""


class ErroArquivo(QuestiAIError):
    """Falha ao ler ou gravar o arquivo de dados (permissão, disco, etc.)."""


class DadosCorrompidos(QuestiAIError):
    """O dados.json existe, mas não é um JSON válido ou tem estrutura errada."""


class UsuarioJaExiste(QuestiAIError):
    """Tentativa de cadastrar um nome que já existe."""


class UsuarioNaoEncontrado(QuestiAIError):
    """Operação sobre um usuário que não está na base."""


# =====================================================================
# 1. CAMADA DE DADOS
# =====================================================================

ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados.json")


def _fazer_backup():
    """Copia o dados.json com data e hora no nome. Devolve uma mensagem."""
    backup = f"{ARQUIVO}.{datetime.now():%Y%m%d-%H%M%S}.bak"
    try:
        shutil.copy(ARQUIVO, backup)
        return f"Uma cópia foi salva como {os.path.basename(backup)}."
    except OSError:
        return "Não foi possível criar uma cópia de segurança."


def _estrutura_valida(dados):
    """usuarios e escolas precisam ser listas de registros (dicionários)."""
    return all(
        isinstance(dados[chave], list) and all(isinstance(item, dict) for item in dados[chave])
        for chave in ("usuarios", "escolas")
    )


def carregar_dados():
    if not os.path.exists(ARQUIVO):
        return {"usuarios": [], "escolas": []}

    try:
        # utf-8-sig lê arquivos com ou sem BOM (comum no Bloco de Notas)
        with open(ARQUIVO, "r", encoding="utf-8-sig") as f:
            dados = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        if isinstance(e, json.JSONDecodeError):
            detalhe = f"linha {e.lineno}"
        else:
            detalhe = "codificação inválida, o esperado é UTF-8"
        raise DadosCorrompidos(
            f"O arquivo {os.path.basename(ARQUIVO)} está corrompido ({detalhe}). "
            f"{_fazer_backup()}"
        ) from e
    except OSError as e:
        raise ErroArquivo(f"Não foi possível ler o arquivo de dados: {e}") from e

    if not isinstance(dados, dict):
        raise DadosCorrompidos("O formato do arquivo de dados é inválido.")

    dados.setdefault("usuarios", [])
    dados.setdefault("escolas", [])
    if not _estrutura_valida(dados):
        raise DadosCorrompidos(
            "A estrutura do arquivo de dados é inválida: 'usuarios' e 'escolas' "
            "devem ser listas de registros."
        )
    return dados


def salvar_dados(dados):
    temp = ARQUIVO + ".tmp"
    try:
        # Grava num temporário e troca no final: se algo falhar no meio,
        # o arquivo original continua intacto.
        with open(temp, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        os.replace(temp, ARQUIVO)
    except (OSError, TypeError) as e:
        if os.path.exists(temp):
            try:
                os.remove(temp)
            except OSError:
                pass
        raise ErroArquivo(f"Não foi possível salvar os dados: {e}") from e


def normalizar(texto):
    """Minúsculas, sem espaços nas pontas e sem acentos. Aceita qualquer tipo."""
    texto = "" if texto is None else str(texto)
    texto = texto.strip().lower()
    sem_acento = unicodedata.normalize("NFD", texto)
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")


def _mesmo_nome(usuario, nome):
    return normalizar(usuario.get("nome")) == normalizar(nome)


def buscar_usuario(nome):
    dados = carregar_dados()
    for usuario in dados["usuarios"]:
        if _mesmo_nome(usuario, nome):
            return usuario
    return None


def adicionar_usuario(usuario):
    dados = carregar_dados()
    if any(_mesmo_nome(u, usuario["nome"]) for u in dados["usuarios"]):
        raise UsuarioJaExiste(f"O nome '{usuario['nome']}' já está cadastrado.")
    dados["usuarios"].append(usuario)
    salvar_dados(dados)


def adicionar_escola(estado, cidade, escola):
    dados = carregar_dados()
    ja_existe = any(
        normalizar(e.get("escola")) == normalizar(escola)
        and normalizar(e.get("cidade")) == normalizar(cidade)
        and normalizar(e.get("estado")) == normalizar(estado)
        for e in dados["escolas"]
    )
    if ja_existe:
        return False
    dados["escolas"].append({"estado": estado, "cidade": cidade, "escola": escola})
    salvar_dados(dados)
    return True


def listar_usuarios(tipo=None):
    dados = carregar_dados()
    if tipo is None:
        return dados["usuarios"]
    return [u for u in dados["usuarios"] if u.get("tipo") == tipo]


def atualizar_usuario(nome, novos_dados):
    dados = carregar_dados()
    for usuario in dados["usuarios"]:
        if _mesmo_nome(usuario, nome):
            usuario.update(novos_dados)
            salvar_dados(dados)
            return
    raise UsuarioNaoEncontrado(f"Usuário '{nome}' não encontrado.")


def excluir_usuario(nome):
    dados = carregar_dados()
    antes = len(dados["usuarios"])
    dados["usuarios"] = [u for u in dados["usuarios"] if not _mesmo_nome(u, nome)]
    if len(dados["usuarios"]) == antes:
        raise UsuarioNaoEncontrado(f"Usuário '{nome}' não encontrado.")
    salvar_dados(dados)


# =====================================================================
# 2. ENTRADA DE DADOS (com validação)
# =====================================================================

def pedir_texto(msg):
    """Repete a pergunta até receber algo que não seja vazio."""
    while True:
        valor = input(msg).strip()
        if valor:
            return valor
        print("Este campo não pode ficar vazio.")


def pedir_inteiro(msg, minimo=None, maximo=None):
    """Repete a pergunta até receber um número inteiro dentro dos limites."""
    while True:
        bruto = input(msg).strip()
        try:
            if "_" in bruto:  # o int() aceitaria "1_0" como 10
                raise ValueError
            valor = int(bruto)
        except ValueError:
            print("Digite apenas números inteiros.")
            continue

        if minimo is not None and valor < minimo:
            print(f"Valor inválido: o valor mínimo é {minimo}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"Valor inválido: o valor máximo é {maximo}.")
            continue

        return valor


def pedir_confirmacao(msg):
    """Repete a pergunta até receber uma resposta afirmativa ou negativa."""
    # normalizar() já tira os acentos, então "não" chega aqui como "nao"
    sim_opcoes = {"sim", "s"}
    nao_opcoes = {"nao", "n"}

    while True:
        resposta = normalizar(input(msg))
        if resposta in sim_opcoes:
            return True
        if resposta in nao_opcoes:
            return False
        print("Responda com 'sim' ou 'não'.")


def pedir_tipo():
    """Repete a pergunta até receber 'aluno' ou 'professor'."""
    while True:
        resposta = normalizar(input("Você é aluno ou professor? "))
        if resposta in ("aluno", "professor"):
            return resposta
        print("Opção inválida. Digite 'aluno' ou 'professor'.")


def pedir_nome_novo():
    """Pergunta o nome e recusa já de início se ele já estiver cadastrado."""
    nome = pedir_texto("Seu nome: ")
    if buscar_usuario(nome) is not None:
        raise UsuarioJaExiste(f"O nome '{nome}' já está cadastrado.")
    return nome


def criar_usuario():
    nome = pedir_nome_novo()
    escola = pedir_texto("Qual sua escola: ")
    ano = pedir_inteiro("Qual seu ano: ", minimo=1)
    turma = pedir_texto("Qual sua turma: ")
    professor = pedir_texto("Qual é seu professor: ")
    return nome, escola, turma, professor, ano


def criar_professor():
    nome = pedir_nome_novo()
    escola = pedir_texto("Em qual escola você dá aula: ")
    materia = pedir_texto("Qual matéria você dá aula: ")
    turma = pedir_texto("Em qual turma você dá aula: ")
    return nome, escola, materia, turma


def criar_escola():
    estado = pedir_texto("Estado da sua escola: ")
    cidade = pedir_texto("Cidade da sua escola: ")
    escola = pedir_texto("Nome da sua escola: ")
    return estado, cidade, escola


# =====================================================================
# 3. MENU DO USUÁRIO LOGADO
# =====================================================================

def menu_usuario(usuario):
    """Menu que se repete até o usuário escolher sair (ou excluir a conta)."""
    while True:
        print("\n--- MENU ---")
        print("1 - Listar usuários")
        print("2 - Atualizar meus dados")
        print("3 - Excluir minha conta")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        try:
            if opcao == "1":
                for u in listar_usuarios():
                    print(f"- {u.get('nome', '?')} ({u.get('tipo', '?')}) "
                          f"| escola: {u.get('escola', 'não informada')}")

            elif opcao == "2":
                campos = [c for c in usuario if c not in ("nome", "tipo")]
                if not campos:
                    print("Não há campos para alterar.")
                    continue
                print("Campos que você pode alterar:", ", ".join(campos))
                campo = input("Qual campo quer alterar? ").strip().lower()
                if campo in campos:
                    if campo == "ano":
                        valor = pedir_inteiro("Novo valor para ano: ", minimo=1)
                    else:
                        valor = pedir_texto(f"Novo valor para {campo}: ")
                    atualizar_usuario(usuario["nome"], {campo: valor})
                    usuario[campo] = valor
                    print("Dados atualizados!")
                else:
                    print("Campo inválido.")

            elif opcao == "3":
                if pedir_confirmacao("Tem certeza que quer excluir sua conta? (sim/não) "):
                    excluir_usuario(usuario["nome"])
                    print("Conta excluída.")
                    break
                print("Exclusão cancelada.")

            elif opcao == "0":
                print("Até logo!")
                break

            else:
                print("Opção inválida.")

        except UsuarioNaoEncontrado as e:
            # Ex.: o registro foi apagado por fora enquanto o menu estava aberto
            print(f"Erro: {e}")
            break
        except ErroArquivo as e:
            # Falha de disco não derruba o menu: o usuário pode tentar de novo
            print(f"Erro: {e}")


# =====================================================================
# 4. FLUXO PRINCIPAL
# =====================================================================

def fazer_login():
    nome_login = pedir_texto("Digite seu nome completo: ")
    usuario = buscar_usuario(nome_login)

    if usuario is None:
        print("Nome não encontrado. Reinicie e faça seu cadastro.")
        return

    nome = usuario.get("nome", nome_login)
    escola = usuario.get("escola", "não informada")
    tipo = usuario.get("tipo")

    if tipo == "aluno":
        print(f"Bem vindo de volta, {nome}! Você é da escola {escola} "
              f"e seu professor é o {usuario.get('professor', 'não informado')}")
    elif tipo == "professor":
        print(f"Bem vindo de volta, professor {nome}! Você dá aula de "
              f"{usuario.get('materia', 'não informada')} na turma "
              f"{usuario.get('turma', 'não informada')} da escola {escola}")
    else:
        print(f"Bem vindo de volta, {nome}! Aviso: seu cadastro está sem um tipo "
              f"válido (aluno ou professor). Você pode excluir a conta no menu "
              f"e se cadastrar de novo.")
    menu_usuario(usuario)


def cadastrar_aluno():
    try:
        nome, escola, turma, professor, ano = criar_usuario()
        novo = {
            "nome": nome,
            "tipo": "aluno",
            "escola": escola,
            "turma": turma,
            "professor": professor,
            "ano": ano,
        }
        adicionar_usuario(novo)
    except UsuarioJaExiste:
        print("Esse nome já está cadastrado. Faça login.")
        return

    print(f"Bem vindo {nome}, você é da escola {escola} e seu professor é o {professor}")
    menu_usuario(novo)


def cadastrar_professor():
    try:
        nome, escola, materia, turma = criar_professor()
        novo = {
            "nome": nome,
            "tipo": "professor",
            "escola": escola,
            "materia": materia,
            "turma": turma,
        }
        adicionar_usuario(novo)
    except UsuarioJaExiste:
        print("Esse nome já está cadastrado. Faça login.")
        return

    print(f"Bem vindo professor {nome}, você dá aula na escola {escola} "
          f"da materia {materia} na turma {turma}")

    if pedir_confirmacao("Você gostaria de adicionar uma nova escola? (sim/não) "):
        estado, cidade, escola_nova = criar_escola()
        try:
            if adicionar_escola(estado, cidade, escola_nova):
                print(f"A escola {escola_nova} que fica em {estado}, {cidade} foi adicionada!")
            else:
                print("Essa escola já estava cadastrada.")
        except ErroArquivo as e:
            print(f"Erro: {e}")

    menu_usuario(novo)


def main():
    print("Bem vindo ao QuestiAI!!")
    if pedir_confirmacao("Você já possui login? (sim/não) "):
        fazer_login()
    elif pedir_tipo() == "aluno":
        cadastrar_aluno()
    else:
        cadastrar_professor()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma encerrado.")
    except DadosCorrompidos as e:
        print(f"\nErro grave: {e}")
        sys.exit(1)
    except QuestiAIError as e:
        print(f"\nErro: {e}")
        sys.exit(1)