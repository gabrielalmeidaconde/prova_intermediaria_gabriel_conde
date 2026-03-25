from flask import Flask, request, jsonify, abort
from db import db
from models import Transacao
import requests
import os

app = Flask(__name__)

QUEUE_NAME = "transacao-queue"
CACHE_TTL = 300  # 5 minutos
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql://appuser:apppass@localhost:5432/transacoes")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Helper para validar usuário
def get_user_info(user_id):
    try:
        user_id = str(user_id).strip()

        # 1) tenta listar todos os usuários
        resp = requests.get("http://18.228.48.67/users", timeout=5)
        if resp.status_code != 200:
            abort(502, description="Erro ao consultar serviço de usuários")

        usuarios = resp.json()

        # 2) procura o usuário pelo id
        for user in usuarios:
            if str(user.get("id")) == user_id:
                return user

        return None

    except requests.RequestException:
        abort(502, description="Erro ao consultar serviço de usuários")

@app.route("/transacao", methods=["GET"])
def listar_transacoes():
    user_id = request.args.get("id")
    if user_id:
        transacoes = Transacao.query.filter_by(user_id=user_id).all()
    else:
        transacoes = Transacao.query.all()
    return jsonify([t.to_dict() for t in transacoes]), 200

@app.route("/transacao/<string:transacao_id>", methods=["DELETE"])
def deletar_transacao(transacao_id):
    transacao = Transacao.query.get(transacao_id)
    if not transacao:
        abort(404, description="Transação não encontrada")
    db.session.delete(transacao)
    db.session.commit()
    return jsonify({"message": "Transação deletada"}), 200

@app.route("/transacao", methods=["POST"])
def criar_transacao():
    data = request.get_json()
    user_id = data.get("user_id")
    codigo_acao = data.get("codigo_acao")
    quantidade = data.get("quantidade")
    preco_unitario = data.get("preco_unitario")
    data_transacao = data.get("data_transacao")

    if not all([user_id, codigo_acao, quantidade, preco_unitario, data_transacao]):
        abort(400, description="Dados incompletos")

    user_info = get_user_info(user_id)
    if not user_info:
        abort(404, description="Usuário não encontrado")


    valor_total = float(quantidade) * float(preco_unitario)
    transacao = Transacao(
        user_id=user_id,
        user_email=user_info["email"],
        codigo_acao=codigo_acao,
        quantidade=quantidade,
        preco_unitario=preco_unitario,
        valor_total=valor_total,
        data_transacao=data_transacao
    )
    db.session.add(transacao)
    db.session.commit()
    return jsonify(transacao.to_dict()), 201

if __name__ == "__main__":
    app.run(debug=True)
