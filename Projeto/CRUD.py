from funções import (pedir_texto, pedir_senha, ler_senha, pedir_professor_existente,
                     pedir_dados_aluno, pedir_dados_professor, pedir_dados_escola)
from gerenciar_dados import (normalizar, gerar_hash_senha, verificar_senha,
                             buscar_usuario, adicionar_usuario, listar_alunos_do_professor,
                             atualizar_usuario, excluir_usuario,
                             listar_escolas, adicionar_escola)

# Campos que cada tipo de usuário pode alterar no próprio perfil
CAMPOS_EDITAVEIS = {
    "aluno": ["escola", "turma", "professor", "ano"],
    "professor": ["escola", "materia", "turma"],
}


# ---------- Ações do menu ----------

def mostrar_dados(usuario):
    print(f"\nNome: {usuario['nome']}")
    for campo in CAMPOS_EDITAVEIS[usuario["tipo"]]:
        print(f"{campo.capitalize()}: {usuario.get(campo, '-')}")


def atualizar_meus_dados(usuario):
    campos = CAMPOS_EDITAVEIS[usuario["tipo"]]
    print("Campos que você pode alterar:", ", ".join(campos))
    campo = normalizar(input("Qual campo quer alterar? "))
    if campo not in campos:
        print("Campo inválido.")
        return

    if campo == "professor":
        valor = pedir_professor_existente()
        if valor is None:
            print("Alteração cancelada.")
            return
    else:
        valor = pedir_texto(f"Novo valor para {campo}: ")

    atualizar_usuario(usuario["id"], {campo: valor})
    usuario[campo] = valor
    print("Dados atualizados!")


def trocar_senha(usuario):
    senha = pedir_senha()
    atualizar_usuario(usuario["id"], {"senha": gerar_hash_senha(senha)})
    print("Senha alterada!")



def excluir_minha_conta(usuario):
    """Retorna True se a conta foi excluída."""

    if usuario["tipo"] == "professor":
        alunos = listar_alunos_do_professor(usuario["nome"])

        if alunos:
            print(f"Você tem {len(alunos)} aluno(s) vinculados.")
            print("Transfira os alunos antes de excluir sua conta.")
            return False

    confirma = normalizar(input("Tem certeza que quer excluir sua conta? (sim/não) "))

    if confirma in ("sim", "s"):
        if excluir_usuario(usuario["id"]):
            print("Conta excluída.")
            return True

        print("Não foi possível excluir a conta.")
        return False

    print("Ok, sua conta foi mantida.")
    return False



def ver_meus_alunos(professor):
    alunos = listar_alunos_do_professor(professor["nome"])
    if not alunos:
        print("Você ainda não tem alunos cadastrados.")
        return
    print(f"\nSeus alunos ({len(alunos)}):")
    for a in alunos:
        print(f"- {a['nome']} | turma: {a['turma']} | ano: {a['ano']}")


def ver_escolas():
    escolas = listar_escolas()
    if not escolas:
        print("Nenhuma escola cadastrada.")
        return
    for e in escolas:
        print(f"- {e['escola']} ({e['cidade']}, {e['estado']})")


def cadastrar_escola():
    estado, cidade, escola = pedir_dados_escola()
    if adicionar_escola(estado, cidade, escola):
        print(f"A escola {escola}, em {cidade}, {estado}, foi adicionada!")
    else:
        print("Essa escola já está cadastrada.")


# ---------- Menus ----------

def menu_aluno(aluno):
    while True:
        print("\n--- MENU DO ALUNO ---")
        print("1 - Ver meus dados")
        print("2 - Atualizar meus dados")
        print("3 - Trocar senha")
        print("4 - Excluir minha conta")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            mostrar_dados(aluno)
        elif opcao == "2":
            atualizar_meus_dados(aluno)
        elif opcao == "3":
            trocar_senha(aluno)
        elif opcao == "4":
            if excluir_minha_conta(aluno):
                break
        elif opcao == "0":
            print("Até logo!")
            break
        else:
            print("Opção inválida.")


def menu_professor(professor):
    while True:
        print("\n--- MENU DO PROFESSOR ---")
        print("1 - Ver meus alunos")
        print("2 - Ver meus dados")
        print("3 - Ver escolas cadastradas")
        print("4 - Adicionar escola")
        print("5 - Atualizar meus dados")
        print("6 - Trocar senha")
        print("7 - Excluir minha conta")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            ver_meus_alunos(professor)
        elif opcao == "2":
            mostrar_dados(professor)
        elif opcao == "3":
            ver_escolas()
        elif opcao == "4":
            cadastrar_escola()
        elif opcao == "5":
            atualizar_meus_dados(professor)
        elif opcao == "6":
            trocar_senha(professor)
        elif opcao == "7":
            if excluir_minha_conta(professor):
                break
        elif opcao == "0":
            print("Até logo!")
            break
        else:
            print("Opção inválida.")


def abrir_menu(usuario):
    if usuario["tipo"] == "aluno":
        menu_aluno(usuario)
    else:
        menu_professor(usuario)


# ---------- Login e cadastro ----------

def boas_vindas(usuario):
    if usuario["tipo"] == "aluno":
        print(f"Bem vindo de volta, {usuario['nome']}! Você é da escola {usuario['escola']} "
              f"e seu professor é o {usuario['professor']}")
    else:
        print(f"Bem vindo de volta, professor {usuario['nome']}! Você dá aula de "
              f"{usuario['materia']} na turma {usuario['turma']} da escola {usuario['escola']}")


def fazer_login():
    """Retorna o usuário logado ou None."""
    nome = pedir_texto("Digite seu nome completo: ")
    usuario = buscar_usuario(nome)

    if usuario is None:
        print("Nome não encontrado. Escolha a opção de cadastro.")
        return None

    # Contas antigas, criadas antes de existir senha
    if not usuario.get("senha"):
        print("Sua conta ainda não tem senha. Crie uma agora.")
        usuario["senha"] = gerar_hash_senha(pedir_senha())
        atualizar_usuario(usuario["id"], {"senha": usuario["senha"]})
        return usuario

    for _ in range(3):
        if verificar_senha(ler_senha("Senha: "), usuario["senha"]):
            return usuario
        print("Senha incorreta.")
    print("Muitas tentativas. Voltando ao início.")
    return None


def cadastrar():
    """Retorna o novo usuário ou None se o cadastro não foi concluído."""
    tipo = normalizar(input("Você é aluno ou professor? "))
    if tipo not in ("aluno", "professor"):
        print("Opção inválida. Digite 'aluno' ou 'professor'.")
        return None

    # O nome é conferido antes das outras perguntas
    nome = pedir_texto("Digite seu nome completo: ")
    if buscar_usuario(nome):
        print("Esse nome já está cadastrado. Faça login.")
        return None

    dados = pedir_dados_aluno() if tipo == "aluno" else pedir_dados_professor()
    if dados is None:
        print("Cadastro cancelado.")
        return None

    senha = pedir_senha()
    usuario = adicionar_usuario({"nome": nome, "tipo": tipo, **dados,
                                 "senha": gerar_hash_senha(senha)})

    if tipo == "aluno":
        print(f"Bem vindo {nome}, você é da escola {usuario['escola']} "
              f"e seu professor é o {usuario['professor']}")
    else:
        print(f"Bem vindo professor {nome}, você dá aula na escola {usuario['escola']} "
              f"da matéria {usuario['materia']} na turma {usuario['turma']}")
        resposta = normalizar(input("Você gostaria de adicionar uma nova escola? (sim/não) "))
        if resposta in ("sim", "s"):
            cadastrar_escola()

    return usuario


# ---------- Programa principal ----------

def main():
    print("Bem vindo ao QuestiAI!!")
    while True:
        print("\n1 - Já tenho login")
        print("2 - Quero me cadastrar")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            usuario = fazer_login()
            if usuario:
                boas_vindas(usuario)
                abrir_menu(usuario)
        elif opcao == "2":
            usuario = cadastrar()
            if usuario:
                abrir_menu(usuario)
        elif opcao == "0":
            print("Até logo!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()