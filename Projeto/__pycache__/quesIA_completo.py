"""
QuestiAI - cadastro e login de alunos e professores.

Uso (dentro da pasta do projeto):
    python3 questiai.py             inicia o programa
    python3 questiai.py --popular   recria o dados.json com dados fictícios (demonstração)

Organização do arquivo, na ordem em que as partes dependem umas das outras:
1. Arquivo (JSON)          carregar_dados / salvar_dados
2. Texto e senhas          normalizar / gerar_hash_senha / verificar_senha
3. CRUD de usuários        buscar, adicionar, listar, atualizar, excluir
4. Escolas                 buscar, adicionar, listar
5. Entrada de dados        perguntar..., criar_usuario / criar_professor / criar_escola
6. Fluxos e menu           cadastrar, fazer_login, menu_usuario, menu_inicial, main
7. Dados de demonstração   popular
"""
import hashlib
import hmac
import json
import os
import shutil
import sys
import unicodedata

ARQUIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados.json")
CAMPOS_PROTEGIDOS = ("nome", "tipo", "id", "senha", "pontos")  # o usuário não edita direto
ITERACOES_HASH = 100_000
TAMANHO_MINIMO_SENHA = 4
MAX_TENTATIVAS_LOGIN = 3


# =====================================================================
# 1. ARQUIVO (JSON)
# =====================================================================
def dados_vazios():
    return {"usuarios": [], "escolas": []}


def carregar_dados():
    """Lê o dados.json. Se não existir, devolve dados vazios; se estiver
    corrompido, guarda uma cópia em dados.json.bak antes de seguir."""
    if not os.path.exists(ARQUIVO):
        return dados_vazios()
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if not isinstance(dados, dict):
            raise TypeError("Estrutura raiz inválida no JSON.")
        dados.setdefault("usuarios", [])
        dados.setdefault("escolas", [])
        return dados
    except (json.JSONDecodeError, OSError, AttributeError, TypeError):
        print("Erro ao ler o arquivo de dados. Uma cópia dele foi guardada em dados.json.bak.")
        try:
            shutil.copy(ARQUIVO, ARQUIVO + ".bak")
        except OSError:
            pass
        return dados_vazios()


def salvar_dados(dados):
    """Grava em um arquivo temporário e troca no final, para não deixar o
    dados.json pela metade se algo falhar durante a escrita."""
    temporario = ARQUIVO + ".tmp"
    try:
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        os.replace(temporario, ARQUIVO)
        return True
    except OSError:
        print("Erro ao salvar os dados.")
        if os.path.exists(temporario):
            try:
                os.remove(temporario)
            except OSError:
                pass
        return False


# =====================================================================
# 2. TEXTO E SENHAS
# =====================================================================
def normalizar(texto):
    """Minúsculas, sem espaços nas pontas e sem acentos (para comparar nomes)."""
    texto = texto.strip().lower()
    sem_acento = unicodedata.normalize("NFD", texto)
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")


def calcular_hash(senha, salt_hex):
    return hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        bytes.fromhex(salt_hex),
        ITERACOES_HASH,
    ).hex()


def gerar_hash_senha(senha):
    """Devolve 'salt$hash'. Cada chamada gera um salt novo."""
    salt_hex = os.urandom(16).hex()
    return f"{salt_hex}${calcular_hash(senha, salt_hex)}"


def verificar_senha(senha, armazenado):
    try:
        salt_hex, hash_guardado = armazenado.split("$", 1)
        return hmac.compare_digest(calcular_hash(senha, salt_hex), hash_guardado)
    except (ValueError, AttributeError):
        return False


# =====================================================================
# 3. CRUD DE USUÁRIOS
# =====================================================================
def _adicionar_usuario_na_memoria(dados, usuario):
    """Adiciona usuário ao dicionário `dados` em memória. Retorna True/False."""
    alvo = normalizar(usuario["nome"])
    if any(normalizar(u["nome"]) == alvo for u in dados["usuarios"]):
        return False
    usuario["id"] = max((u.get("id", 0) for u in dados["usuarios"]), default=0) + 1
    dados["usuarios"].append(usuario)
    return True


def buscar_usuario(nome):  # READ (um)
    alvo = normalizar(nome)
    for usuario in carregar_dados()["usuarios"]:
        if normalizar(usuario["nome"]) == alvo:
            return usuario
    return None


def buscar_professor(nome):
    usuario = buscar_usuario(nome)
    if usuario is not None and usuario.get("tipo") == "professor":
        return usuario
    return None


def adicionar_usuario(usuario):  # CREATE
    """Recebe o dicionário já com a senha em hash. Gera o id e recusa nome repetido."""
    dados = carregar_dados()
    if not _adicionar_usuario_na_memoria(dados, usuario):
        return False
    return salvar_dados(dados)


def listar_usuarios(tipo=None, escola=None):  # READ (vários), sem expor a senha
    usuarios = carregar_dados()["usuarios"]
    if tipo is not None:
        usuarios = [u for u in usuarios if u.get("tipo") == tipo]
    if escola is not None:
        escola_alvo = normalizar(escola)
        usuarios = [u for u in usuarios if normalizar(u.get("escola", "")) == escola_alvo]
    return [{k: v for k, v in u.items() if k != "senha"} for u in usuarios]


def atualizar_usuario(nome, novos_dados):  # UPDATE
    campos_invalidos = [c for c in CAMPOS_PROTEGIDOS if c != "senha"]
    if any(campo in campos_invalidos for campo in novos_dados):
        return False
    dados = carregar_dados()
    alvo = normalizar(nome)
    for usuario in dados["usuarios"]:
        if normalizar(usuario["nome"]) == alvo:
            usuario.update(novos_dados)
            return salvar_dados(dados)
    return False


def excluir_usuario(nome):  # DELETE
    dados = carregar_dados()
    alvo = normalizar(nome)
    antes = len(dados["usuarios"])
    dados["usuarios"] = [u for u in dados["usuarios"] if normalizar(u["nome"]) != alvo]
    if len(dados["usuarios"]) < antes:
        return salvar_dados(dados)
    return False


# =====================================================================
# 4. ESCOLAS
# =====================================================================
def _adicionar_escola_na_memoria(dados, estado, cidade, escola):
    """Adiciona escola ao dicionário `dados` em memória. Retorna True/False."""
    for existente in dados["escolas"]:
        if (
            normalizar(existente["escola"]) == normalizar(escola)
            and normalizar(existente["cidade"]) == normalizar(cidade)
        ):
            return False
    dados["escolas"].append({"estado": estado, "cidade": cidade, "escola": escola})
    return True


def listar_escolas():
    return carregar_dados()["escolas"]


def buscar_escola(nome):
    alvo = normalizar(nome)
    for escola in listar_escolas():
        if normalizar(escola["escola"]) == alvo:
            return escola
    return None


def adicionar_escola(estado, cidade, escola):
    dados = carregar_dados()
    if not _adicionar_escola_na_memoria(dados, estado, cidade, escola):
        return False
    return salvar_dados(dados)


# =====================================================================
# 5. ENTRADA DE DADOS
# =====================================================================
def perguntar(texto):
    """Repete a pergunta até a resposta não ser vazia."""
    while True:
        resposta = input(f"{texto}: ").strip()
        if resposta:
            return resposta
        print("Este campo não pode ficar vazio.")


def perguntar_sim_nao(pergunta):
    """Repete a pergunta até a resposta ser sim ou não. Retorna True para sim."""
    while True:
        resposta = normalizar(input(f"{pergunta} (sim/não) "))
        if resposta in ("sim", "s"):
            return True
        if resposta in ("nao", "n"):
            return False
        print("Resposta inválida. Digite 'sim' ou 'não'.")


def perguntar_tipo():
    while True:
        tipo = normalizar(input("Você é aluno ou professor? "))
        if tipo in ("aluno", "professor"):
            return tipo
        print("Opção inválida. Digite 'aluno' ou 'professor'.")


def pedir_senha_nova():
    """Pede a senha duas vezes (visível no terminal)."""
    while True:
        senha = input("Crie uma senha: ").strip()
        if len(senha) < TAMANHO_MINIMO_SENHA:
            print(f"A senha deve ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres.")
        elif input("Confirme a senha: ").strip() != senha:
            print("As senhas não coincidem.")
        else:
            return senha


def perguntar_escola_existente():
    """Só aceita uma escola já cadastrada e devolve o nome como está guardado."""
    while True:
        escola = buscar_escola(perguntar("Qual sua escola"))
        if escola is not None:
            return escola["escola"]
        nomes = ", ".join(e["escola"] for e in listar_escolas()) or "nenhuma cadastrada"
        print(f"Escola não cadastrada. Escolas disponíveis: {nomes}")
        print("Peça ao seu professor para cadastrar a escola.")


def perguntar_escola_para_professor():
    """Busca a escola informada; se não existir, permite cadastrar na hora."""
    while True:
        nome_digitado = perguntar("Em qual escola você dá aula")
        escola = buscar_escola(nome_digitado)
        if escola is not None:
            return escola["escola"]

        nomes = ", ".join(e["escola"] for e in listar_escolas()) or "nenhuma cadastrada"
        print(f"Escola '{nome_digitado}' ainda não cadastrada. Escolas disponíveis: {nomes}")
        if perguntar_sim_nao("Deseja cadastrar essa escola agora?"):
            estado = perguntar("Estado da escola")
            cidade = perguntar("Cidade da escola")
            if perguntar_sim_nao(f"Usar o nome '{nome_digitado}' para a escola?"):
                nome_escola = nome_digitado
            else:
                nome_escola = perguntar("Nome oficial da escola")

            if adicionar_escola(estado, cidade, nome_escola):
                print(f"Escola '{nome_escola}' ({cidade}, {estado}) cadastrada!")
                return buscar_escola(nome_escola)["escola"]
            print("Não foi possível cadastrar a escola (verifique se já existe na mesma cidade).")


def perguntar_professor_da_escola(escola):
    """Só aceita um professor cadastrado e que dê aula na escola informada."""
    while True:
        professor = buscar_professor(perguntar("Qual é seu professor"))
        if professor is None:
            print("Professor não encontrado. Confira o nome completo.")
        elif normalizar(professor.get("escola", "")) != normalizar(escola):
            print("Esse professor não dá aula nessa escola.")
        else:
            return professor["nome"]


def criar_usuario():
    """Dados do aluno. Retorna uma tupla (escola, turma, professor, ano)."""
    escola = perguntar_escola_existente()
    while True:
        try:
            ano = int(perguntar("Qual seu ano (apenas o número)"))
            if ano > 0:
                break
        except ValueError:
            pass
        print("Digite apenas números para o ano.")
    turma = perguntar("Qual sua turma")
    professor = perguntar_professor_da_escola(escola)
    return escola, turma, professor, f"{ano}º ano"


def criar_professor():
    """Dados do professor. Retorna uma tupla (escola, materia, turma)."""
    escola = perguntar_escola_para_professor()
    materia = perguntar("Qual matéria você dá aula")
    turma = perguntar("Em qual turma você dá aula")
    return escola, materia, turma


def criar_escola():
    """Dados de uma escola nova. Retorna uma tupla (estado, cidade, escola)."""
    estado = perguntar("Estado da sua escola")
    cidade = perguntar("Cidade da sua escola")
    escola = perguntar("Nome da sua escola")
    return estado, cidade, escola


# =====================================================================
# 6. FLUXOS E MENU
# =====================================================================
def cadastrar():
    """Cadastro completo. Retorna o dicionário do novo usuário, ou None se falhar."""
    tipo = perguntar_tipo()
    nome = perguntar("Seu nome completo")
    if buscar_usuario(nome):
        print("Esse nome já está cadastrado. Faça login.")
        return None

    if tipo == "aluno":
        escola, turma, professor, ano = criar_usuario()
        novo = {
            "nome": nome,
            "tipo": "aluno",
            "escola": escola,
            "turma": turma,
            "professor": professor,
            "ano": ano,
            "trilha": "Não definida",
            "pontos": 0,
        }
    else:
        escola, materia, turma = criar_professor()
        novo = {
            "nome": nome,
            "tipo": "professor",
            "escola": escola,
            "materia": materia,
            "turma": turma,
        }

    novo["senha"] = gerar_hash_senha(pedir_senha_nova())
    if not adicionar_usuario(novo):
        print("Não foi possível concluir o cadastro.")
        return None
    return novo


def fazer_login():
    """Pede nome e senha (até 3 tentativas). Retorna o usuário ou None."""
    nome = perguntar("Digite seu nome completo")
    usuario = buscar_usuario(nome)
    if usuario is None:
        print("Nome não encontrado. Faça seu cadastro.")
        return None

    for tentativa in range(MAX_TENTATIVAS_LOGIN):
        senha = input("Senha: ").strip()
        if verificar_senha(senha, usuario.get("senha", "")):
            return usuario
        restantes = MAX_TENTATIVAS_LOGIN - tentativa - 1
        if restantes:
            print(f"Senha incorreta. Tentativas restantes: {restantes}")
    print("Número de tentativas excedido.")
    return None


def mensagem_boas_vindas(usuario, volta=False):
    prefixo = "Bem vindo de volta" if volta else "Bem vindo"
    if usuario["tipo"] == "aluno":
        print(
            f"{prefixo}, {usuario['nome']}! Você é da escola {usuario['escola']} "
            f"e seu professor é o {usuario['professor']}"
        )
    else:
        print(
            f"{prefixo}, professor {usuario['nome']}! Você dá aula de "
            f"{usuario['materia']} na turma {usuario['turma']} da escola {usuario['escola']}"
        )


def oferecer_nova_escola():
    if perguntar_sim_nao("Você gostaria de adicionar uma nova escola?"):
        estado, cidade, escola_nova = criar_escola()
        if adicionar_escola(estado, cidade, escola_nova):
            print(f"A escola {escola_nova} que fica em {cidade}, {estado} foi adicionada!")
        else:
            print("Não foi possível adicionar a escola (ela pode já existir).")
    else:
        print("Ok, seguindo para o menu.")


def validar_alteracao(campo, valor, usuario):
    """Valida o novo valor conforme o campo e o perfil do usuário.
    Devolve o valor aceito ou None."""
    if campo == "escola":
        escola = buscar_escola(valor)
        return escola["escola"] if escola else None
    if campo == "professor":
        professor = buscar_professor(valor)
        if professor is None:
            return None
        if usuario.get("tipo") == "aluno" and normalizar(professor.get("escola", "")) != normalizar(
            usuario.get("escola", "")
        ):
            return None
        return professor["nome"]
    return valor


def menu_usuario(usuario):
    """Menu que se repete até o usuário escolher sair (ou excluir a conta)."""
    while True:
        print("\n--- MENU ---")
        print("1 - Listar usuários da escola")
        print("2 - Atualizar meus dados")
        print("3 - Excluir minha conta")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            for u in listar_usuarios(escola=usuario.get("escola")):
                print(f"- {u.get('nome')} ({u.get('tipo')}) | turma: {u.get('turma', '-')}")

        elif opcao == "2":
            campos = [c for c in usuario if c not in CAMPOS_PROTEGIDOS] + ["senha"]
            print("Campos que você pode alterar:", ", ".join(campos))
            campo = input("Qual campo quer alterar? ").strip().lower()
            if campo not in campos:
                print("Campo inválido.")
                continue

            if campo == "senha":
                nova_senha = pedir_senha_nova()
                alteracoes = {"senha": gerar_hash_senha(nova_senha)}
            else:
                valor = validar_alteracao(campo, perguntar(f"Novo valor para {campo}"), usuario)
                if valor is None:
                    if campo == "professor" and usuario.get("tipo") == "aluno":
                        print("Valor inválido: o professor precisa existir e dar aula na sua escola.")
                    else:
                        print(f"Valor inválido para {campo}: não consta no cadastro.")
                    continue

                alteracoes = {campo: valor}
                if campo == "escola" and usuario.get("tipo") == "aluno":
                    prof_atual = buscar_professor(usuario.get("professor", ""))
                    if prof_atual is None or normalizar(prof_atual.get("escola", "")) != normalizar(valor):
                        print("Seu professor atual não pertence à nova escola.")
                        novo_prof = perguntar_professor_da_escola(valor)
                        alteracoes["professor"] = novo_prof

            if atualizar_usuario(usuario["nome"], alteracoes):
                usuario.update(alteracoes)
                print("Dados atualizados!")
            else:
                print("Não foi possível atualizar os dados.")

        elif opcao == "3":
            if perguntar_sim_nao("Tem certeza que quer excluir sua conta?"):
                if excluir_usuario(usuario["nome"]):
                    print("Conta excluída.")
                    break
                print("Não foi possível excluir a conta.")

        elif opcao == "0":
            print("Até logo!")
            break

        else:
            print("Opção inválida.")


def menu_inicial():
    """Menu inicial para login, cadastro ou saída."""
    while True:
        print("\n=== QUESTIAI ===")
        print("1 - Fazer login")
        print("2 - Cadastrar")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            usuario = fazer_login()
            if usuario is not None:
                mensagem_boas_vindas(usuario, volta=True)
                menu_usuario(usuario)

        elif opcao == "2":
            novo = cadastrar()
            if novo is not None:
                mensagem_boas_vindas(novo)
                if novo["tipo"] == "professor":
                    oferecer_nova_escola()
                menu_usuario(novo)

        elif opcao == "0":
            print("Até logo!")
            break

        else:
            print("Opção inválida.")


def main():
    print("Bem vindo ao QuestiAI!!")
    menu_inicial()


# =====================================================================
# 7. DADOS DE DEMONSTRAÇÃO (python3 questiai.py --popular)
#    Todos os nomes são inventados. A senha de todo mundo é SENHA_DEMO.
# =====================================================================
SENHA_DEMO = "1234"

ESCOLAS = [
    # estado, cidade, escola
    ("Pernambuco", "Recife", "Escola Modelo Aprender"),
]

PROFESSORES = [
    # nome, escola, matéria, turma
    ("Helena Barbosa", "Escola Modelo Aprender", "Matemática", "7A"),
    ("Rafael Montenegro", "Escola Modelo Aprender", "Português", "7B"),
    ("Patrícia Cavalcanti", "Escola Modelo Aprender", "Ciências", "8A"),
]

ALUNOS = [
    # nome, escola, turma, professor, ano, trilha, pontos
    ("Ana Beatriz Souza", "Escola Modelo Aprender", "7A", "Helena Barbosa", "7º ano", "Frações", 120),
    ("Bruno Henrique Lima", "Escola Modelo Aprender", "7A", "Helena Barbosa", "7º ano", "Frações", 85),
    ("Camila Ferreira", "Escola Modelo Aprender", "7A", "Helena Barbosa", "7º ano", "Geometria", 200),
    ("Davi Albuquerque", "Escola Modelo Aprender", "7A", "Helena Barbosa", "7º ano", "Frações", 40),
    ("Eduarda Pires", "Escola Modelo Aprender", "7B", "Rafael Montenegro", "7º ano", "Interpretação de texto", 150),
    ("Felipe Andrade", "Escola Modelo Aprender", "7B", "Rafael Montenegro", "7º ano", "Gramática", 95),
    ("Gabriela Neves", "Escola Modelo Aprender", "7B", "Rafael Montenegro", "7º ano", "Interpretação de texto", 175),
    ("Heitor Vasconcelos", "Escola Modelo Aprender", "7B", "Rafael Montenegro", "7º ano", "Gramática", 60),
    ("Isabela Rocha", "Escola Modelo Aprender", "8A", "Patrícia Cavalcanti", "8º ano", "Corpo humano", 130),
    ("João Pedro Melo", "Escola Modelo Aprender", "8A", "Patrícia Cavalcanti", "8º ano", "Ecologia", 110),
    ("Larissa Duarte", "Escola Modelo Aprender", "8A", "Patrícia Cavalcanti", "8º ano", "Corpo humano", 210),
    ("Mateus Cordeiro", "Escola Modelo Aprender", "8A", "Patrícia Cavalcanti", "8º ano", "Ecologia", 70),
]


def dados_demo_consistentes():
    """Confere se todo aluno aponta para um professor e uma escola que existem na lista."""
    professores = {p[0] for p in PROFESSORES}
    escolas = {e[2] for e in ESCOLAS}
    for nome, escola, _turma, professor, *_ in ALUNOS:
        if professor not in professores or escola not in escolas:
            print(f"Dado inconsistente: {nome} aponta para professor ou escola inexistente.")
            return False
    return True


def popular():
    """Apaga o dados.json atual (guardando cópia em .bak) e cria os dados fictícios."""
    if not dados_demo_consistentes():
        return False
    if os.path.exists(ARQUIVO):
        try:
            shutil.copy(ARQUIVO, ARQUIVO + ".bak")
        except OSError:
            print("Não foi possível criar o backup. Nada foi alterado.")
            return False

    dados = dados_vazios()
    escolas_ok = sum(_adicionar_escola_na_memoria(dados, *e) for e in ESCOLAS)

    usuarios_ok = 0
    for nome, escola, materia, turma in PROFESSORES:
        usuarios_ok += _adicionar_usuario_na_memoria(
            dados,
            {
                "nome": nome,
                "tipo": "professor",
                "escola": escola,
                "materia": materia,
                "turma": turma,
                "senha": gerar_hash_senha(SENHA_DEMO),
            },
        )
    for nome, escola, turma, professor, ano, trilha, pontos in ALUNOS:
        usuarios_ok += _adicionar_usuario_na_memoria(
            dados,
            {
                "nome": nome,
                "tipo": "aluno",
                "escola": escola,
                "turma": turma,
                "professor": professor,
                "ano": ano,
                "trilha": trilha,
                "pontos": pontos,
                "senha": gerar_hash_senha(SENHA_DEMO),
            },
        )

    esperado = (len(ESCOLAS), len(PROFESSORES) + len(ALUNOS))
    if (escolas_ok, usuarios_ok) != esperado:
        print(f"Atenção: só {escolas_ok} escola(s) e {usuarios_ok} usuário(s) foram gravados.")
        return False
    if not salvar_dados(dados):
        return False

    print(
        f"Pronto! {len(PROFESSORES)} professores, {len(ALUNOS)} alunos e "
        f"{len(ESCOLAS)} escola(s) criados."
    )
    print(f"Senha de todos: {SENHA_DEMO}")
    print("Para testar, entre com: Helena Barbosa (professora) ou Ana Beatriz Souza (aluna).")
    return True


def main_popular():
    resposta = input("Isso APAGA o dados.json atual e cria dados fictícios. Continuar? (sim/não) ")
    if normalizar(resposta) in ("sim", "s"):
        popular()
    else:
        print("Nada foi alterado.")


if __name__ == "__main__":
    try:
        if "--popular" in sys.argv:
            main_popular()
        else:
            main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma encerrado.")