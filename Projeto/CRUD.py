from funções import criar_escola, criar_professor, criar_usuario
print("Bem vindo ao QuestiAI!!")
acao = input("Você é aluno ou professor? ").lower()

if acao == "aluno":
    nome, escola, turma, professor, ano = criar_usuario()
    print(f"Bem vindo {nome}, você é da escola {escola} e seu professor é o {professor}")

elif acao == "professor":
    nome, escola, materia, turma = criar_professor()
    print(f"Bem vindo professor {nome}, você dá aula na escola {escola} da materia {materia} na turma {turma}")
    acao = input("Você gostaria de adicionar uma nova escola? ").lower()

    if acao == "sim":
        estado, cidade, escola = criar_escola()
        print(f"a escola {escola} que fica em {estado}, {cidade} foi adicionada!")
    elif acao == "não":
        print("Ok, você será redirecionado para o início")
    else:
        print("erro, volte ao início")
