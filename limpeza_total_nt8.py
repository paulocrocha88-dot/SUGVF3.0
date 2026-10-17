import os
import argparse

def remove_duplicates(directories, patterns):
    for directory in directories:
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}")
            continue

        print(f"Scanning directory: {directory}")
        for root, _, files in os.walk(directory):
            for file in files:
                for pattern in patterns:
                    if file.endswith(pattern):
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                            print(f"Deleted: {file_path}")
                        except Exception as e:
                            print(f"Failed to delete {file_path}: {e}")
                        break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove duplicate files in specified directories.")
    parser.add_argument("directories", nargs="+", help="Target directories to scan")
    parser.add_argument("--patterns", nargs="+", default=["(1).cs", "- Copia.cs", ".bak"], help="File patterns/extensions to delete")

    args = parser.parse_args()

    remove_duplicates(args.directories, args.patterns)
