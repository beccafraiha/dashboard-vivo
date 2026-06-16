# Dashboard Inteligente de Monitoramento Logístico

## Arquivos
- `app.py` — código do dashboard (Streamlit)
- `dados.csv` — base de dados de exemplo (50 entregas)
- `requirements.txt` — dependências

## Como executar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Como publicar (link público gratuito)

1. Crie um repositório **público** no GitHub e envie estes 3 arquivos.
2. Acesse https://share.streamlit.io e faça login com sua conta GitHub.
3. Clique em **"New app"**.
4. Selecione o repositório, branch `main` e arquivo principal `app.py`.
5. Clique em **"Deploy!"**.
6. Em poucos minutos você receberá um link como:
   `https://seu-app.streamlit.app`

Esse link é público e não exige login para acesso.

## Substituindo os dados reais
Basta substituir o conteúdo de `dados.csv`, mantendo as mesmas colunas:
`ID Entrega, Data, Região, Transportadora, Prazo Previsto, Data Real, Dias de Atraso, Status`
