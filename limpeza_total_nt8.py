import os
import sys
import re

def clean_onedrive_duplicates(directory):
    duplicate_patterns = [
        re.compile(r'^(.*?)\s\(\d+\)(\.[^.]+)$'), # file (1).ext
        re.compile(r'^(.*?)\s-\sCopy(\.[^.]+)$'), # file - Copy.ext
        re.compile(r'^(.*?)\s-\sCopia(\.[^.]+)$'), # file - Copia.ext
        re.compile(r'^(.*?)\s-\sCópia(\.[^.]+)$'), # file - Cópia.ext
        # Regex for -DESKTOP-ABC type suffixes is removed to avoid false positives.
        # Alternatively, we could strictly look for specific known computer names.
    ]

    count = 0

    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return

    for root, dirs, files in os.walk(directory):
        for filename in files:
            for p in duplicate_patterns:
                match = p.match(filename)
                if match:
                    original_name = match.group(1) + match.group(2)
                    original_path = os.path.join(root, original_name)

                    if os.path.exists(original_path):
                        filepath = os.path.join(root, filename)
                        print(f"Removendo ficheiro duplicado: {filepath}")
                        try:
                            os.remove(filepath)
                            count += 1
                        except Exception as e:
                            print(f"Erro ao apagar {filepath}: {e}")
                    else:
                        print(f"Possível duplicado encontrado {filename}, mas o original {original_name} não existe. Ignorando.")
                    break

    print(f"Limpeza concluída! {count} ficheiros duplicados removidos na pasta {directory}.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = os.path.expanduser("~/Documents/NinjaTrader 8/bin/Custom")
        print(f"Nenhum diretório fornecido. A usar o caminho por defeito: {target_dir}")

    clean_onedrive_duplicates(target_dir)
