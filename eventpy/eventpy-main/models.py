import sys
from datetime import datetime
from peewee import *
from config.database_config import db
from werkzeug.security import generate_password_hash, check_password_hash

class BaseModel(Model):
    class Meta:
        database = db

class Utilizador(BaseModel):
    nome = CharField()
    email = CharField(unique=True)
    is_admin = BooleanField(default=False)
    telefone = CharField()
    documento_identificacao = CharField()
    senha_hash = CharField()
    criado_em = DateTimeField(default=datetime.now)
    email_validado = BooleanField(default=False)
    token_validacao = CharField(null=True)
    
    def set_senha(self, senha):
        # Em produção, usar criptografia AES
        import hashlib
        self.senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
    def verificar_senha(self, senha):
        import hashlib
        return self.senha_hash == hashlib.sha256(senha.encode()).hexdigest()

class TipoResiduo(BaseModel):
    """Classificação dos tipos de REEE"""
    nome = CharField()
    descricao = TextField()
    icone = CharField()  # Nome do ícone (ex: fa-mobile, fa-laptop)
    exemplos = TextField()  # Exemplos em formato JSON
    
    class Meta:
        table_name = 'tipos_residuo'

class PontoRecolha(BaseModel):
    """Pontos de recolha de REEE em Lisboa"""
    nome = CharField()
    morada = CharField()
    freguesia = CharField()
    bairro = CharField(null=True)
    latitude = DecimalField(decimal_places=8, max_digits=11)
    longitude = DecimalField(decimal_places=8, max_digits=11)
    
    # Horários de funcionamento
    horario_abertura = TimeField()
    horario_fecho = TimeField()
    dias_funcionamento = CharField()  # Ex: "2ª a 6ª", "Sábado", etc.
    
    # Tipos de resíduos aceites (relacionamento)
    tipos_aceites = ManyToManyField(TipoResiduo, backref='pontos_recolha')
    
    # Informações adicionais
    telefone = CharField(null=True)
    email = CharField(null=True)
    website = CharField(null=True)
    observacoes = TextField(null=True)
    
    # Tipo de ponto
    TIPO_CENTRO_RECECAO = "centro_rececao"
    TIPO_ECOCENTRO = "ecocentro"
    TIPO_ENTRAJUDA = "entrajuda"
    TIPO_PONTO_ELETRAO = "ponto_eletrao"
    TIPO_RECOLHA_MUNICIPAL = "recolha_municipal"
    
    tipo_ponto = CharField(choices=[
        (TIPO_CENTRO_RECECAO, "Centro de Receção"),
        (TIPO_ECOCENTRO, "Ecocentro"),
        (TIPO_ENTRAJUDA, "Entrajuda"),
        (TIPO_PONTO_ELETRAO, "Ponto Eletrão"),
        (TIPO_RECOLHA_MUNICIPAL, "Recolha Municipal")
    ])
    
    ativo = BooleanField(default=True)
    criado_em = DateTimeField(default=datetime.now)
    atualizado_em = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'pontos_recolha'
    
    def get_tipo_ponto_display(self):
        """Retorna o display name para o tipo de ponto"""
        tipo_map = {
            self.TIPO_CENTRO_RECECAO: "Centro de Receção",
            self.TIPO_ECOCENTRO: "Ecocentro",
            self.TIPO_ENTRAJUDA: "Entrajuda",
            self.TIPO_PONTO_ELETRAO: "Ponto Eletrão",
            self.TIPO_RECOLHA_MUNICIPAL: "Recolha Municipal"
        }
        return tipo_map.get(self.tipo_ponto, self.tipo_ponto)

class Notificacao(BaseModel):
    """Notificações para utilizadores sobre novos pontos"""
    utilizador = ForeignKeyField(Utilizador, backref='notificacoes')
    ponto_recolha = ForeignKeyField(PontoRecolha, backref='notificacoes')
    mensagem = TextField()
    enviada_em = DateTimeField(default=datetime.now)
    lida = BooleanField(default=False)
    
    class Meta:
        table_name = 'notificacoes'

class Contato(BaseModel):
    """Mensagens de contacto/envio de sugestões"""
    nome = CharField()
    email = CharField()
    assunto = CharField()
    mensagem = TextField()
    data_envio = DateTimeField(default=datetime.now)
    respondido = BooleanField(default=False)
    
    class Meta:
        table_name = 'contatos'

# Configurar a relação many-to-many
PontoRecolhaTiposResiduo = PontoRecolha.tipos_aceites.get_through_model()