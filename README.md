# Monitoring Serial

## Como gerar o arquivo Executável (.exe)

Para transformar este projeto Python em um executável autônomo (que pode ser aberto com dois cliques, sem precisar de Python instalado e sem abrir janela do terminal), utilizamos a biblioteca `pyinstaller`.

### 1. Pré-requisitos
Certifique-se de estar com o ambiente virtual (venv) ativado e instale o PyInstaller e a biblioteca de imagens caso não tenha:
```bash
pip install pyinstaller pillow
```

### 2. Comando de Compilação
Rode o seguinte comando na raiz do projeto:
```bash
pyinstaller --clean --onefile --windowed --icon="app_icon.ico" main.py
```
**Explicação das flags:**
- `--clean`: Limpa o cache de compilações anteriores, prevenindo bugs de arquivos residuais.
- `--onefile`: Empacota todo o código e bibliotecas (como matplotlib e pandas) em um único e limpo arquivo `.exe`.
- `--windowed`: Garante que a aplicação abra direto na interface gráfica, ocultando o console/terminal preto de fundo.
- `--icon="app_icon.ico"`: Define o nosso ícone customizado de monitoramento para o arquivo gerado.

### ⚠️ Resolução de Problemas (Troubleshooting)
Se você se deparar com erros de **"ModuleNotFoundError"** (ex: módulo `graphic` não encontrado) após compilar, siga estes passos antes de rodar o comando novamente:
1. **Apague o arquivo `main.spec`**: O PyInstaller cria este arquivo na primeira execução. Se ele já existir, o comando ignorará atualizações e reciclará o cache antigo.
2. **Apague qualquer arquivo `__init__.py` na raiz do projeto**: Ter um `__init__.py` solto na mesma pasta do seu script principal (`main.py`) confunde o mapa de rotas do PyInstaller, impedindo que ele localize os arquivos vizinhos da mesma pasta.