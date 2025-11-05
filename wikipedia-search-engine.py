import subprocess
import sys

# Metoda uruchamiająca dany skrypt
def run_script(script_path):
    print(f"Launching {script_path}...")
    result = subprocess.run([sys.executable, script_path])
    
    if result.returncode == 0:
        sys.exit()

def main():
    run_script("crawler.py")

if __name__ == "__main__":
    main()
    # URL_prefix = "https://pl.wikipedia.org/wiki/"

    # while True:
    #     URL_sufix = input(f"Podaj adres strony ('x' aby zakończyć)\n{URL_prefix}")

    #     if URL_sufix[0] == 'x':
    #         break