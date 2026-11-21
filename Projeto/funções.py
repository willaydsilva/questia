"""Funções que pedem dados ao usuário, já com validação."""
from getpass import getpass

from gerenciar_dados import buscar_professor

TAMANHO_MINIMO_SENHA = 4
MOSTRAR_SENHA = True  # True: a senha aparece enquanto digita (bom para a demonstração)


def ler_senha(mensagem):
    if MOSTRAR_SENHA:
        return input(mensagem)
    return getpass(mensagem)


def pedir_texto(mensagem):
    """Repete a pergunta até a pessoa digitar algo."""
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("Este campo não pode ficar vazio.")


def pedir_senha(confirmar=True):
    while True:
        senha = ler_senha(f"Senha (mínimo {TAMANHO_MINIMO_SENHA} caracteres): ")
        if len(senha) < TAMANHO_MINIMO_SENHA:
            print("Senha muito curta.")
            continue
        if confirmar and ler_senha("Repita a senha: ") != senha:
            print("As senhas não conferem.")
            continue
        return senha


def pedir_professor_existente():
    """Pede o nome de um professor já cadastrado. Digite 0 para cancelar."""
    while True:
        nome = pedir_texto("Nome do seu professor (ou 0 para cancelar): ")
        if nome == "0":
            return None
        professor = buscar_professor(nome)
        if professor:
            return professor["nome"]
        print("Professor não encontrado. Confira o nome ou peça para ele se cadastrar primeiro.")


def pedir_dados_aluno():
    escola = pedir_texto("Escola: ")
    turma = pedir_texto("Turma: ")
    professor = pedir_professor_existente()
    if professor is None:
        return None
    ano = pedir_texto("Ano: ")
    return {"escola": escola, "turma": turma, "professor": professor, "ano": ano}


def pedir_dados_professor():
    escola = pedir_texto("Escola em que você dá aula: ")
    materia = pedir_texto("Matéria: ")
    turma = pedir_texto("Turma: ")
    return {"escola": escola, "materia": materia, "turma": turma}


def pedir_dados_escola():
    estado = pedir_texto("Estado: ")
    cidade = pedir_texto("Cidade: ")
    escola = pedir_texto("Nome da escola: ")
    return estado, cidade, escola
