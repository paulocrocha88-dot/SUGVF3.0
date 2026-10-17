import os
import argparse

def is_duplicate(filename, duplicate_patterns):
    for pattern in duplicate_patterns:
        if filename.endswith(pattern):
            return True
    return False

def is_system_file_to_clean(filename, system_files):
    return filename in system_files

def run_aggressive_cleanup(directories):
    duplicate_patterns = ["(1).cs", "- Copia.cs", ".bak"]
    system_files_to_check = ["ResourceDesigner.cs", "DefaultOptimizer.cs", "GeneticOptimizer.cs", "StrategyGenerator.cs"]
    protected_file = "ZMQSUGFReceiver.cs"

    for directory in directories:
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}")
            continue

        print(f"Scanning directory: {directory}")
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)

                # Regra 3: Manter ZMQSUGFReceiver.cs intacto
                if file == protected_file:
                    print(f"Protected file kept: {file_path}")
                    continue

                should_delete = False
                reason = ""

                # Regra 1 e 2: Apagar duplicados padrão
                if is_duplicate(file, duplicate_patterns):
                    should_delete = True
                    reason = "Duplicate pattern"

                # Regra 2: Apagar ficheiros de sistema que causam CS0101 (duplicados/fora do sítio)
                # Como a instrução diz para fazer uma limpeza agressiva para eliminar CS0101,
                # frequentemente o utilizador apaga todas as cópias destes para que o NT8 as regenere.
                # Se terminam em .cs e estão na lista de problemas, podemos removê-los.
                elif is_system_file_to_clean(file, system_files_to_check):
                    should_delete = True
                    reason = "System file prone to CS0101 conflict"

                if should_delete:
                    try:
                        os.remove(file_path)
                        print(f"Deleted [{reason}]: {file_path}")
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")

if __name__ == "__main__":
    default_dirs = [
        r"C:\Users\paulo\OneDrive\Documentos\NinjaTrader 8\bin\Custom",
        r"C:\Users\paulo\Documents\NinjaTrader 8\bin\Custom"
    ]

    parser = argparse.ArgumentParser(description="Aggressive cleanup for NT8 CS0101 errors.")
    parser.add_argument("directories", nargs="*", default=default_dirs, help="Target directories to scan")

    args = parser.parse_args()

    print("Iniciando limpeza agressiva...")
    run_aggressive_cleanup(args.directories)
    print("Limpeza concluída.")
