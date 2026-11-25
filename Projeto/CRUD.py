from funções import criar_escola, criar_professor, criar_usuario
from gerenciar_dados import (buscar_usuario, adicionar_usuario, adicionar_escola,
                             listar_usuarios, atualizar_usuario, excluir_usuario)


def perguntar_sim_nao(pergunta):
    """Repete a pergunta até a resposta ser sim ou não. Retorna True para sim."""
    while True:
        resposta = input(f"{pergunta} (sim/não) ").strip().lower()
        if resposta in ("sim", "s"):
            return True
        if resposta in ("não", "nao", "n"):
            return False
        print("Resposta inválida. Digite 'sim' ou 'não'.")


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
            usuarios = listar_usuarios()
            if usuario.get("tipo") == "aluno":
                usuarios = [
                    u for u in usuarios
                    if u.get("tipo") == "aluno" and u.get("escola") == usuario.get("escola")
                ]
            elif usuario.get("tipo") == "professor":
                usuarios = [
                    u for u in usuarios
                    if u.get("escola") == usuario.get("escola")
                ]
            for u in usuarios:
                print(f"- {u.get('nome')} ({u.get('tipo')}) | escola: {u.get('escola')}")

        elif opcao == "2":
            campos = [c for c in usuario if c not in ("nome", "tipo")]
            print("Campos que você pode alterar:", ", ".join(campos))
            campo = input("Qual campo quer alterar? ").strip().lower()
            if campo in campos:
                valor = input(f"Novo valor para {campo}: ").strip()
                if atualizar_usuario(usuario["nome"], {campo: valor}):
                    usuario[campo] = valor
                    print("Dados atualizados!")
                else:
                    print("Não foi possível atualizar os dados.")
            else:
                print("Campo inválido.")

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


def main():
    print("Bem vindo ao QuestiAI!!")
    # ---------- CAMINHO 1: JÁ TEM LOGIN ----------
    if perguntar_sim_nao("Você já possui login?"):
        nome_login = input("Digite seu nome completo: ").strip()
        usuario = buscar_usuario(nome_login) if nome_login else None

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
        while acao not in ("aluno", "professor"):
            print("Opção inválida. Digite 'aluno' ou 'professor'.")
            acao = input("Você é aluno ou professor? ").strip().lower()

        if acao == "aluno":
            nome, escola, turma, professor, ano = criar_usuario()

            novo = {
                "nome": nome,
                "tipo": "aluno",
                "escola": escola,
                "turma": turma,
                "professor": professor,
                "ano": ano,
            }

            if not nome.strip():
                print("O nome não pode ficar vazio.")
            elif buscar_usuario(nome):
                print("Esse nome já está cadastrado. Faça login.")
            elif not adicionar_usuario(novo):
                print("Não foi possível concluir o cadastro.")
            else:
                print(f"Bem vindo {nome}, você é da escola {escola} e seu professor é o {professor}")
                menu_usuario(novo)

        elif acao == "professor":
            nome, escola, materia, turma = criar_professor()

            novo = {
                "nome": nome,
                "tipo": "professor",
                "escola": escola,
                "materia": materia,
                "turma": turma,
            }

            if not nome.strip():
                print("O nome não pode ficar vazio.")
            elif buscar_usuario(nome):
                print("Esse nome já está cadastrado. Faça login.")
            elif not adicionar_usuario(novo):
                print("Não foi possível concluir o cadastro.")
            else:
                print(f"Bem vindo professor {nome}, você dá aula na escola {escola} "
                      f"da materia {materia} na turma {turma}")

                if perguntar_sim_nao("Você gostaria de adicionar uma nova escola?"):
                    estado, cidade, escola_nova = criar_escola()
                    if adicionar_escola(estado, cidade, escola_nova):
                        print(f"a escola {escola_nova} que fica em {estado}, {cidade} foi adicionada!")
                    else:
                        print("Não foi possível adicionar a escola.")
                else:
                    print("Ok, você será redirecionado para o início")

                menu_usuario(novo)

        else:
            print("Opção inválida. Digite 'aluno' ou 'professor'.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma encerrado.")
