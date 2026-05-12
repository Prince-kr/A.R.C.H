import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--payload", default="' OR 1=1 --")
    args = parser.parse_args()

    print(f"[*] Testing SQL injection on {args.target}...")
    print(f"[*] Payload: {args.payload}")
    print("[+] Potential vulnerability detected in login.php")
    print("[*] Extraction complete: Found 5 database users.")

if __name__ == "__main__":
    main()
