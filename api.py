from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

app = Flask(__name__)
api = Api(app)

# Criar o mecanismo do banco de dados e a sessão
engine = create_engine('sqlite:///banco_de_dados.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Definir a classe Usuario para mapeamento ORM
class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(String, unique=True)
    nome = Column(String)
    senha = Column(String)

# Definir a classe ContaBancaria para mapeamento ORM
class ContaBancaria(Base):
    __tablename__ = 'contas_bancarias'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(String, unique=True)
    saldo = Column(Float)

# Criar as tabelas no banco de dados
Base.metadata.create_all(engine)

# Funções de verificação de credenciais e saldo
def verificar_credenciais(usuario_id, senha):
    session = Session()
    usuario = session.query(Usuario).filter_by(usuario_id=usuario_id, senha=senha).first()
    session.close()
    return usuario is not None

def verificar_saldo(usuario_id, valor):
    session = Session()
    conta = session.query(ContaBancaria).filter_by(usuario_id=usuario_id).first()
    saldo_suficiente = conta.saldo >= valor if conta else False
    session.close()
    return saldo_suficiente

class Autenticacao(Resource):
    def post(self):
        dados = request.get_json()
        usuario_id = dados['usuario_id']
        senha = dados['senha']
        if verificar_credenciais(usuario_id, senha):
            token = str(uuid.uuid4())
            return {"token": token}, 200
        else:
            return {"mensagem": "Credenciais inválidas"}, 401

class Saldo(Resource):
    def get(self, usuario_id):
        session = Session()
        conta = session.query(ContaBancaria).filter_by(usuario_id=usuario_id).first()
        session.close()
        if conta:
            return {"saldo": conta.saldo}, 200
        else:
            return {"mensagem": "Usuário não encontrado"}, 404

class Transferencia(Resource):
    def post(self):
        dados = request.get_json()
        remetente = dados['remetente']
        destinatario = dados['destinatario']
        valor = float(dados['valor'])

        if verificar_saldo(remetente, valor):
            session = Session()
            conta_remetente = session.query(ContaBancaria).filter_by(usuario_id=remetente).first()
            conta_destinatario = session.query(ContaBancaria).filter_by(usuario_id=destinatario).first()
            conta_remetente.saldo -= valor
            conta_destinatario.saldo += valor
            session.commit()
            session.close()
            return {"mensagem": "Transferência realizada com sucesso"}, 200
        else:
            return {"mensagem": "Saldo insuficiente"}, 400

api.add_resource(Autenticacao, '/autenticacao')
api.add_resource(Saldo, '/saldo/<string:usuario_id>')
api.add_resource(Transferencia, '/transferencia')

if __name__ == '__main__':
    app.run(debug=True)
