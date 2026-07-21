import sys
import os
 
 
def obter_pasta_base():
    """
    Pasta onde ficam os DADOS QUE PRECISAM SER GRAVADOS e
    sobreviver depois que o programa fecha: o banco de dados
    (autoeletrica.db) e os PDFs gerados (OS_PDFs/).
 
    - Rodando como .exe: é a pasta onde o .exe está de verdade
      (ex: Área de Trabalho, ou onde o Emerson salvou o programa).
    - Rodando como script: é a pasta do projeto.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))
 
 
def obter_pasta_recursos():
    """
    Pasta de recursos EMBUTIDOS dentro do .exe, só leitura
    (ex: a logo). No modo --onefile, o PyInstaller extrai esses
    arquivos numa pasta temporária (sys._MEIPASS) toda vez que
    o programa abre.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))
