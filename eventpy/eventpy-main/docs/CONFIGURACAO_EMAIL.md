# Configuração de Email - Reciclagem REEE

## 📧 **Configurar Envio de Emails**

### **🔐 Passo 1: Criar App Password no Gmail**

#### **1. Ativar Verificação em 2 Etapas:**
1. Aceda a: https://myaccount.google.com/security
2. Procure por "Verificação em duas etapas"
3. Ative a verificação em duas etapas

#### **2. Criar App Password:**
1. Aceda a: https://myaccount.google.com/apppasswords
2. Selecione:
   - **App:** "Outro (nome personalizado)"
   - **Nome:** "Reciclagem REEE"
3. Clique em **"Gerar"**
4. **Copie a password** (formato: xxxx xxxx xxxx xxxx xxxx)

---

### **⚙️ Passo 2: Configurar Arquivo .env**

#### **Editar o arquivo `.env`:**
```bash
# Abra o arquivo: .env
# Substitua as configurações abaixo:
```

```env
# Configurações de Email (Gmail)
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_app_password_aqui
```

**Importante:**
- Use seu email real no `MAIL_USERNAME`
- Cole a App Password gerada no `MAIL_PASSWORD`
- **NÃO** use sua password normal do Gmail

---

### **📦 Passo 3: Instalar Dependências**

#### **Instalar Flask-Mail:**
```bash
pip install Flask-Mail==0.9.1
```

#### **Ou instalar todas as dependências:**
```bash
pip install -r requirements.txt
```

---

### **🚀 Passo 4: Testar Envio de Email**

#### **1. Iniciar Aplicação:**
```bash
python app.py
```

#### **2. Registrar Novo Utilizador:**
1. Aceda a: http://localhost:5000/registro
2. Preencha o formulário
3. Verifique seu Gmail

#### **3. Validar Email:**
1. Abra o email recebido
2. Clique no botão "Validar Email"
3. Faça login com suas credenciais

---

### **🔧 Solução de Problemas**

#### **❌ Email não chega:**

**Possíveis causas:**
1. **App Password incorreta**
   - Verifique se copiou corretamente
   - Gere uma nova App Password

2. **Firewall/Antivírus bloqueando**
   - Desative temporariamente para teste
   - Adicione exceção para Python

3. **Spam no Gmail**
   - Verifique a pasta "Spam"
   - Marque como "Não é spam"

#### **❌ Erro de SMTP:**

**Verifique o console:**
```bash
# Procure por mensagens como:
✅ Email enviado com sucesso para email@exemplo.com
❌ Erro ao enviar email: [mensagem de erro]
```

#### **❌ Gmail bloqueando acesso:**

**Solução:**
1. Aceda a: https://accounts.google.com/displayunlockcaptcha
2. Faça login com sua conta Gmail
3. Clique em "Continuar"
4. Tente enviar email novamente

---

### **📱 Teste Rápido**

#### **Script de Teste:**
```python
# Criar arquivo: test_email.py
from app import enviar_email_validacao

# Testar envio
token = "test_token_123"
email = "seu_email@gmail.com"

if enviar_email_validacao(email, token):
    print("✅ Teste de email bem-sucedido!")
else:
    print("❌ Falha no teste de email")
```

#### **Executar teste:**
```bash
python test_email.py
```

---

### **🎯 Configuração Produção**

#### **Para ambiente de produção:**
1. **Use servidor SMTP profissional**
2. **Configure domínio próprio**
3. **Adicione registros SPF/DKIM**
4. **Use variáveis de ambiente seguras**

#### **Exemplo para produção:**
```env
MAIL_SERVER=smtp.seudominio.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=noreply@seudominio.com
MAIL_PASSWORD=senha_segura
```

---

### **✅ Verificação Final**

#### **Após configuração:**
- [ ] App Password criada
- [ ] Arquivo .env configurado
- [ ] Flask-Mail instalado
- [ ] Email de teste recebido
- [ ] Validação de email funcionando
- [ ] Novos utilizadores conseguem registrar

---

### **📞 Suporte**

#### **Se continuar com problemas:**
1. **Verifique logs** no console
2. **Teste com outro email** (Hotmail, Outlook)
3. **Verifique configurações** de rede
4. **Confirme App Password** está correta

**O sistema de emails está pronto para uso!** 🚀
