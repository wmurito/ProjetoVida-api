# Endpoints da API ProjetoVida

## 📋 Resumo

Total de endpoints: **17**
- Públicos: **4**
- Protegidos (requer autenticação): **13**

---

## 🌐 Endpoints Públicos

### 1. Status da API
```
GET /
```
Retorna status online da API.

**Response:**
```json
{"status": "online"}
```

---

### 2. Validar Token
```
POST /auth/validate-token
```
Valida se um token JWT é válido.

**Body:**
```json
{"token": "eyJhbGc..."}
```

**Response:**
```json
{"valid": true}
```

---

### 3. Criar Sessão de Upload (QR Code)
```
POST /create-upload-session
```
Cria sessão para upload via QR Code mobile.

**Rate Limit:** 10/minuto

**Response:**
```json
{
  "session_id": "upload-uuid",
  "upload_url": "/upload-mobile/{session_id}",
  "expires_in": 300
}
```

---

### 4. Upload via Mobile (QR Code)
```
POST /upload-mobile/{session_id}
```
Recebe arquivo do mobile via QR Code.

**Rate Limit:** 5/minuto

**Body:**
```json
{
  "fileName": "termo.pdf",
  "fileType": "application/pdf",
  "fileData": "data:application/pdf;base64,...",
  "cpf": "12345678901"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Arquivo recebido com sucesso",
  "cpf": "12345678901"
}
```

---

## 🔒 Endpoints Protegidos (Requer Autenticação)

### Autenticação

#### 5. Verificar Usuário Atual
```
GET /auth/me
```
Retorna dados do usuário autenticado.

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
{
  "sub": "user-id",
  "email": "user@example.com",
  ...
}
```

---

### Termo de Aceite

#### 6. Upload Termo de Aceite (Desktop)
```
POST /upload-termo-aceite
```
Upload do termo de aceite via desktop.

**Rate Limit:** 10/minuto

**Headers:** `Authorization: Bearer {token}`

**Form Data:**
- `cpf`: string (obrigatório)
- `termo`: File (PDF, JPG, PNG - máx 5MB)

**Response:**
```json
{
  "success": true,
  "message": "Termo de aceite enviado com sucesso",
  "cpf": "12345678901"
}
```

---

#### 7. Verificar Status Upload (QR Code)
```
GET /upload-status/{session_id}
```
Verifica se arquivo foi enviado via mobile.

**Rate Limit:** 60/minuto

**Response:**
```json
{
  "fileName": "termo.pdf",
  "fileType": "application/pdf",
  "fileData": "data:application/pdf;base64,...",
  "cpf": "12345678901",
  "timestamp": "2024-01-01T12:00:00"
}
```

---

### Pacientes (CRUD)

#### 8. Criar Paciente
```
POST /pacientes/
```
Cadastra novo paciente. **Requer termo de aceite enviado previamente.**

**Headers:** `Authorization: Bearer {token}`

**Body:** JSON com dados do paciente (PacienteCreate schema)

**Validações:**
- CPF obrigatório
- Termo de aceite deve existir no S3

**Response:** Objeto Paciente criado

---

#### 9. Listar Pacientes
```
GET /pacientes/?skip=0&limit=100
```
Lista pacientes com paginação.

**Headers:** `Authorization: Bearer {token}`

**Query Params:**
- `skip`: int (default: 0)
- `limit`: int (default: 100, máx: 100)

**Response:** Array de Pacientes

---

#### 10. Buscar Paciente por ID
```
GET /pacientes/{paciente_id}
```
Retorna dados completos de um paciente.

**Headers:** `Authorization: Bearer {token}`

**Response:** Objeto Paciente

---

#### 11. Atualizar Paciente
```
PUT /pacientes/{paciente_id}
```
Atualiza dados de um paciente.

**Headers:** `Authorization: Bearer {token}`

**Body:** JSON com dados do paciente (PacienteCreate schema)

**Response:** Objeto Paciente atualizado

---

#### 12. Deletar Paciente
```
DELETE /pacientes/{paciente_id}
```
Remove um paciente do sistema.

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
{"success": true}
```

---

#### 13. Histórico do Paciente
```
GET /pacientes/{paciente_id}/historico
```
Retorna histórico de alterações do paciente.

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
[
  {
    "id": 1,
    "paciente_id": 123,
    "data_modificacao": "2024-01-01T12:00:00",
    "dados_anteriores": {...}
  }
]
```

---

### Exportação

#### 14. Exportar Pacientes para Excel
```
GET /api/pacientes/exportar_excel
```
Gera e baixa relatório Excel com dados dos pacientes.

**Headers:** `Authorization: Bearer {token}`

**Response:** Arquivo Excel (.xlsx)

---

### Dashboard (Analytics)

#### 15. Distribuição por Estadiamento
```
GET /dashboard/estadiamento
```
Retorna distribuição de pacientes por estadiamento clínico.

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
[
  {"estagio": "I", "total": 10},
  {"estagio": "II", "total": 15}
]
```

---

#### 16. Sobrevida Global
```
GET /dashboard/sobrevida
```
Retorna distribuição de status vital dos pacientes.

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
[
  {"status": "Vivo", "total": 80},
  {"status": "Óbito", "total": 20}
]
```

---

#### 17. Taxa de Recidiva
```
GET /dashboard/recidiva
```
Retorna contagem de recidivas por tipo.

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
[
  {"tipo": "Recidiva Local", "total": 5},
  {"tipo": "Recidiva Regional", "total": 3},
  {"tipo": "Metástase", "total": 8}
]
```

---

#### 18. Média de Tempos (Delta T)
```
GET /dashboard/delta_t
```
Retorna média de dias entre eventos do tratamento.

**Headers:** `Authorization: Bearer {token}`

**Response:**
```json
[
  {"processo": "Diagnóstico → Cirurgia", "media_dias": 45.5},
  {"processo": "Diagnóstico → Início Tratamento", "media_dias": 30.2},
  {"processo": "Primeira Consulta → Diagnóstico", "media_dias": 15.8}
]
```

---

## 🔐 Autenticação

Todos os endpoints protegidos requerem header:
```
Authorization: Bearer {JWT_TOKEN}
```

Token obtido via AWS Cognito.

---

## ⚡ Rate Limiting

| Endpoint | Limite |
|----------|--------|
| `/upload-termo-aceite` | 10/minuto |
| `/create-upload-session` | 10/minuto |
| `/upload-mobile/{session_id}` | 5/minuto |
| `/upload-status/{session_id}` | 60/minuto |

---

## 🎯 Fluxo de Cadastro de Paciente

1. **Enviar Termo de Aceite**
   - Desktop: `POST /upload-termo-aceite`
   - Mobile: `POST /create-upload-session` → QR Code → `POST /upload-mobile/{session_id}`

2. **Cadastrar Paciente**
   - `POST /pacientes/` (valida se termo existe no S3)

3. **Gerenciar Paciente**
   - Listar: `GET /pacientes/`
   - Buscar: `GET /pacientes/{id}`
   - Atualizar: `PUT /pacientes/{id}`
   - Deletar: `DELETE /pacientes/{id}`
   - Histórico: `GET /pacientes/{id}/historico`

---

## 📊 Estrutura de Dados

### PacienteCreate Schema
```json
{
  "nome_completo": "string",
  "cpf": "string (obrigatório)",
  "data_nascimento": "date",
  "prontuario": "string",
  "genero": "string",
  "telefone": "string",
  "email": "string",
  "endereco": {...},
  "historia_patologica": {...},
  "familiares": [...],
  "habitos_vida": {...},
  "paridade": {...},
  "historia_doenca": {...},
  "tratamento": {...},
  "desfecho": {...},
  "tempos_diagnostico": {...}
}
```

---

## 🛡️ Segurança

- CORS configurado para origens permitidas
- Rate limiting em endpoints sensíveis
- Validação de tipos de arquivo (PDF, JPG, PNG)
- Limite de tamanho de arquivo: 5MB
- Criptografia S3: AES256
- ACL privado em todos os uploads
- Sessões de upload expiram em 5 minutos
- Headers de segurança: X-Content-Type-Options, X-Frame-Options, HSTS, etc.

---

## 📝 Notas

- Endpoint `/paciente/view/{paciente_id}` foi removido (duplicado de `/pacientes/{paciente_id}`)
- Todos os termos são salvos em: `s3://bucket/termos/{cpf}/termo_aceite.pdf`
- Uploads temporários (QR Code) em: `s3://bucket/qrcode-uploads/{session_id}.json`
