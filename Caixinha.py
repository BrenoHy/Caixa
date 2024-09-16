import sqlite3
from datetime import datetime
import re
import hashlib

# Função para validar o formato do CEP
def validar_cep(cep):
    padrao_cep = re.compile(r'^\d{5}-\d{3}$')
    return padrao_cep.match(cep) is not None

# Função para criptografar a senha usando hashlib
def criptografar_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Conectar ao banco de dados
conn = sqlite3.connect('caixa_eletronico.db')
cursor = conn.cursor()

# Excluir tabela se ela existir
cursor.execute('DROP TABLE IF EXISTS usuarios')
conn.commit()

# Tabela de Usuários
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        nome TEXT NOT NULL,
        data_nascimento TEXT NOT NULL,
        cpf TEXT UNIQUE NOT NULL,
        rua TEXT NOT NULL,
        numero TEXT NOT NULL,
        bairro TEXT NOT NULL,
        cidade TEXT NOT NULL,
        estado TEXT NOT NULL,
        cep TEXT NOT NULL,
        saldo REAL DEFAULT 0,
        historico TEXT DEFAULT '',
        senha TEXT NOT NULL
    )
''')
conn.commit()

# Cadastro de Usuário
def cadastrar_usuario(nome, data_nascimento, cpf, rua, numero, bairro, cidade, estado, cep, senha):
    if not validar_cep(cep):
        print("Erro: O CEP deve estar no formato XXXXX-XXX.")
        return
    senha_criptografada = criptografar_senha(senha)
    try:
        cursor.execute('''
            INSERT INTO usuarios (nome, data_nascimento, cpf, rua, numero, bairro, cidade, estado, cep, senha)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, data_nascimento, cpf, rua, numero, bairro, cidade, estado, cep, senha_criptografada))
        conn.commit()
        print("Usuário cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("Erro: CPF já cadastrado.")

# Buscar Usuário por CPF
def buscar_usuario_por_cpf(cpf):
    cursor.execute('''
        SELECT * FROM usuarios WHERE cpf = ?
    ''', (cpf,))
    usuario = cursor.fetchone()
    if usuario:
        return usuario
    else:
        return None
    
# Autenticar Usuário
def autenticar_usuario(cpf, senha):
    cursor.execute('''
        SELECT senha FROM usuarios WHERE cpf = ?
    ''', (cpf,))
    resultado = cursor.fetchone()
    if resultado:
        senha_criptografada = criptografar_senha(senha)
        if resultado[0] == senha_criptografada:
            return True
    return False

# Fechar a conexão no final do programa
def fechar_conexao():
    conn.close()

def mostrar_menu():
    print("\nBem-vindo ao Bork!")
    print("1. Consultar Saldo")
    print("2. Sacar")
    print("3. Depósito")
    print("4. Transferência")
    print("5. Histórico de Movimentações")
    print("6. Sair")

# Consultar Saldo
def consultar_saldo(cpf):
    cursor.execute('SELECT saldo FROM usuarios WHERE cpf = ?', (cpf,))
    saldo = cursor.fetchone()[0] # Busca o saldo no banco de dados
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    print(f"\nSaldo atual: R$ {saldo:.2f}")
    registrar_historico(cpf, f"Consulta de saldo: R$ {saldo:.2f}") # Registrando a consulta de saldo no histórico
    return saldo

# Registrar Histórico
def registrar_historico(cpf, descricao):
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    descricao_com_timestamp = f"{timestamp} - {descricao}\n"
    
    # Verificando o histórico antes de atualizar
    cursor.execute('SELECT historico FROM usuarios WHERE cpf = ?', (cpf))
    historico_atual = cursor.fetchone()[0]

    if historico_atual is None:
        historico_atual = "" # Se estiver vazio, inicialize com uma string vazia

    print(f"Histórico antes da atualização:\n{historico_atual}") # Print de verificação

    # Atualizando histórico
    cursor.execute('''
        UPDATE usuarios
        SET historico = historico || ?
        WHERE cpf = ?
''', (descricao_com_timestamp, cpf))
    conn.commit()

    # Verificando se a atualização foi bem-sucedida
    cursor.execute('SELECT historico FROM usuarios WHERE cpf = ?', (cpf,))
    historico_atualizado = cursor.fetchone()[0]
    print(f"Histórico atualizado\n{historico_atualizado}") # Print para verificar


# Sacar Dinheiro
def sacar_dinheiro(cpf, valor):
    # Verifica o saldo atual do usuário no banco de dados
    cursor.execute('SELECT saldo FROM usuarios WHERE cpf = ?', (cpf,))
    resultado = cursor.fetchone()

    if resultado is None:
        print("Usuário não encontrado.")
        return
    
    saldo_atual = resultado[0]


    # Verifica se o valor de saque é válido
    if valor <= 0:
        print("O valor deve ser maior do que zero.")
    elif valor > saldo_atual:
        print("Saldo insuficiente.")
    else:
        # Atualiza o saldo do usuário no banco de dados
        novo_saldo = saldo_atual - valor
        cursor.execute('UPDATE usuarios SET saldo = ? WHERE cpf = ?', (novo_saldo, cpf))
        conn.commit()

        # Registra a operação no histórico
        registrar_historico(cpf, f"Saque de R$ {valor:.2f}")

        print(f"Saque de R$ {valor:.2f} realizado com sucesso! Saldo atual: R$ {novo_saldo:.2f}")

# Depositar Dinheiro
def depositar_dinheiro(cpf, valor): 
    cursor.execute('SELECT saldo FROM usuarios WHERE cpf = ?', (cpf,))
    resultado = cursor.fetchone()

    if resultado is None:
        print("Usuário não encontrado.")
        return
    
    saldo_atual = resultado[0]

    if valor <= 0:
        print("O valor digitado deve ser maior do que zero.")
    else:
        novo_saldo = saldo_atual + valor
        cursor.execute('UPDATE usuarios SET saldo = ? WHERE cpf = ?', (novo_saldo, cpf))
        conn.commit()

        # Registrando o depósito no histórico
        registrar_historico(cpf, f"Depósito de R$ {valor:.2f}")

        print(f"Depósito de R$ {valor:.2f} realizado com sucesso!")

# Ver Histórico
def ver_historico(cpf):
    cursor.execute('SELECT historico FROM usuarios WHERE cpf = ?', (cpf,))
    resultado = cursor.fetchone()
    if resultado:
        historico = resultado[0]
        print("\nHistórico de Movimentações:")
        if not historico:
            print("Nenhuma movimentação realizada.")
        else:
            print(historico)
    else:
        print("Usuário não encontrado.")

# Transferir Dinheiro
def transferir_dinheiro(cpf_origem, cpf_destino, valor):
    cursor.execute('SELECT saldo FROM usuarios WHERE cpf = ?', (cpf_origem,))
    saldo_origem = cursor.fetchone()
    cursor.execute('SELECT saldo FROM usuarios WHERE cpf = ?', (cpf_destino,))
    saldo_destino = cursor.fetchone()

    if saldo_origem is None or saldo_destino is None:
        print("Usuário(s) não encontrado(s).")
        return

    saldo_origem = saldo_origem[0]
    saldo_destino = saldo_destino[0]

    if valor <= 0:
        print("O valor deve ser maior que zero.")
    elif valor > saldo_origem:
        print("Saldo insuficiente.")
    else:
        novo_saldo_origem = saldo_origem - valor
        novo_saldo_destino = saldo_destino + valor
        cursor.execute('UPDATE usuarios SET saldo = ? WHERE cpf = ?', (novo_saldo_origem, cpf_origem))
        cursor.execute('UPDATE usuarios SET saldo = ? WHERE cpf = ?', (novo_saldo_destino, cpf_destino))
        conn.commit()

        # Registra a operação no histórico
        registrar_historico(cpf_origem, f"Transferência de R$ {valor:.2f} para {cpf_destino}")
        registrar_historico(cpf_destino, f"Transferência recebida de R$ {valor:.2f} de {cpf_origem}")

        print(f"Transferência de R$ {valor:.2f} para {cpf_destino} realizada com sucesso!")

def main():
    while True:
        print("\n1. Criar Conta\n2. Login\n3. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            nome = input("Nome: ")
            data_nascimento = input("Data de nascimento (DD/MM/AAAA): ")
            cpf = input("CPF: ")
            rua = input("Rua: ")
            numero = input("Número: ")
            bairro = input("Bairro: ")
            cidade = input("Cidade: ")
            estado = input("Estado: ")
            cep = input("CEP (XXXXX-XXX): ")
            senha = input("Senha: ")
            cadastrar_usuario(nome, data_nascimento, cpf, rua, numero, bairro, cidade, estado, cep, senha)
        elif opcao == '2':
            cpf = input("Digite o CPF para continuar: ")
            senha = input("Digite sua senha: ")
            if autenticar_usuario(cpf, senha):
                usuario = buscar_usuario_por_cpf(cpf)
                if usuario:
                    while True:
                        mostrar_menu()
                        opcao_usuario = input("Escolha uma opção: ")

                        if opcao_usuario == '1':
                            consultar_saldo(cpf)
                        elif opcao_usuario == '2':
                            valor = float(input("Digite o valor que deseja sacar: "))
                            sacar_dinheiro(cpf, valor)
                        elif opcao_usuario == '3':
                            valor = float(input("Digite o valor que deseja depositar: "))
                            depositar_dinheiro(cpf, valor)
                        elif opcao_usuario == '4':
                            cpf_destino = input("Digite o CPF do destinatário: ")
                            valor = float(input("Digite o valor que deseja transferir: "))
                            transferir_dinheiro(cpf, cpf_destino, valor)
                        elif opcao_usuario == '5':
                            ver_historico(cpf)
                        elif opcao_usuario == '6':
                            print("Obrigado por usar o Bork. Até logo!")
                            break
                        else: 
                            print("Opção inválida! Por favor, selecione outra opção.")
                else:
                    print("Senha incorreta.")
            else:
                print("Usuário não encontrado.")
        elif opcao == '3':
            print("Saindo... Até logo!")
            break
        else:
            print("Opção inválida! Por favor, escolha outra opção.")

if __name__ == "__main__":
    main()
    fechar_conexao()
