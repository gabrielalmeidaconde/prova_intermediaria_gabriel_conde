import uuid
from decimal import Decimal
from db import db


class Transacao(db.Model):
    __tablename__ = "transacoes"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, index=True)
    user_email = db.Column(db.String(120), nullable=False)
    codigo_acao = db.Column(db.String(50), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    valor_total = db.Column(db.Numeric(12, 2), nullable=False)
    data_transacao = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "codigo_acao": self.codigo_acao,
            "quantidade": self.quantidade,
            "preco_unitario": float(self.preco_unitario),
            "valor_total": float(self.valor_total),
            "data_transacao": self.data_transacao.isoformat() if self.data_transacao else None,
        }