import subprocess
import sys

# Metoda uruchamiająca dany skrypt
def run_script(script_path):
    print(f"Launching {script_path}...")
    result = subprocess.run([sys.executable, script_path])
    
    if result.returncode == 2:
        sys.exit(0)
        
    if result.returncode != 0:
        print(f"Błąd przy uruchamianiu {script_path}")
        sys.exit(result.returncode)

def main():
    while True:
        command = input(
            "[S] -> Start programu\n" \
            "[T] -> Uruchom testy\n" \
            "[x] -> Zakończ działanie\n" \
            "> ")
        if command[0] == 'S':        
            run_script("crawler.py")
            run_script("indexer.py")
            run_script("search_engine.py")
        elif command[0] == 'T':
            run_script("indexer_test.py")
            run_script("search_engine_test.py")
        elif command[0] == 'x':
            break

if __name__ == "__main__":
    main()  