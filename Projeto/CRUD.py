from funções import criar_escola, criar_professor, criar_usuario
from gerenciar_dados import (buscar_usuario, adicionar_usuario, adicionar_escola,
                             listar_usuarios, atualizar_usuario, excluir_usuario)


def menu_usuario(usuario):
    """Menu que se repete até o usuário escolher sair (ou excluir a conta)."""
    while True:
        print("\n--- MENU ---")
        print("1 - Listar usuários")
        print("2 - Atualizar meus dados")
        print("3 - Excluir minha conta")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            for u in listar_usuarios():
                print(f"- {u['nome']} ({u['tipo']}) | escola: {u['escola']}")

        elif opcao == "2":
            campos = [c for c in usuario if c not in ("nome", "tipo")]
            print("Campos que você pode alterar:", ", ".join(campos))
            campo = input("Qual campo quer alterar? ").strip().lower()
            if campo in campos:
                valor = input(f"Novo valor para {campo}: ").strip()
                atualizar_usuario(usuario["nome"], {campo: valor})
                usuario[campo] = valor
                print("Dados atualizados!")
            else:
                print("Campo inválido.")

        elif opcao == "3":
            confirma = input("Tem certeza que quer excluir sua conta? (sim/não) ").strip().lower()
            if confirma in ("sim", "s"):
                excluir_usuario(usuario["nome"])
                print("Conta excluída.")
                break

        elif opcao == "0":
            print("Até logo!")
            break

        else:
            print("Opção inválida.")


print("Bem vindo ao QuestiAI!!")
tem_login = input("Você já possui login? (sim/não) ").strip().lower()

# ---------- CAMINHO 1: JÁ TEM LOGIN ----------
if tem_login in ("sim", "s"):
    nome_login = input("Digite seu nome completo: ")
    usuario = buscar_usuario(nome_login)

    if usuario is None:
        print("Nome não encontrado. Reinicie e faça seu cadastro.")
    elif usuario["tipo"] == "aluno":
        print(f"Bem vindo de volta, {usuario['nome']}! Você é da escola {usuario['escola']} "
              f"e seu professor é o {usuario['professor']}")
        menu_usuario(usuario)
    else:
        print(f"Bem vindo de volta, professor {usuario['nome']}! Você dá aula de "
              f"{usuario['materia']} na turma {usuario['turma']} da escola {usuario['escola']}")
        menu_usuario(usuario)

# ---------- CAMINHO 2: CADASTRO ----------
else:
    acao = input("Você é aluno ou professor? ").strip().lower()

    if acao == "aluno":
        nome, escola, turma, professor, ano = criar_usuario()

        if buscar_usuario(nome):
            print("Esse nome já está cadastrado. Faça login.")
        else:
            novo = {
                "nome": nome,
                "tipo": "aluno",
                "escola": escola,
                "turma": turma,
                "professor": professor,
                "ano": ano,
            }
            adicionar_usuario(novo)
            print(f"Bem vindo {nome}, você é da escola {escola} e seu professor é o {professor}")
            menu_usuario(novo)

    elif acao == "professor":
        nome, escola, materia, turma = criar_professor()

        if buscar_usuario(nome):
            print("Esse nome já está cadastrado. Faça login.")
        else:
            novo = {
                "nome": nome,
                "tipo": "professor",
                "escola": escola,
                "materia": materia,
                "turma": turma,
            }
            adicionar_usuario(novo)
            print(f"Bem vindo professor {nome}, você dá aula na escola {escola} "
                  f"da materia {materia} na turma {turma}")

            nova_escola = input("Você gostaria de adicionar uma nova escola? ").strip().lower()
            if nova_escola in ("sim", "s"):
                estado, cidade, escola_nova = criar_escola()
                adicionar_escola(estado, cidade, escola_nova)
                print(f"a escola {escola_nova} que fica em {estado}, {cidade} foi adicionada!")
            elif nova_escola in ("não", "nao", "n"):
                print("Ok, você será redirecionado para o início")
            else:
                print("erro, volte ao início")

            menu_usuario(novo)

    else:
        print("Opção inválida. Digite 'aluno' ou 'professor'.")