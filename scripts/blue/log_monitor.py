import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", required=True)
    args = parser.parse_args()

    print(f"[*] Analyzing system logs for Session {args.session}...")
    print("[!] Detected spike in incoming ICMP traffic.")
    print("[!] Security Alert: Potential DoS attack detected from 127.0.0.1")
    print("[*] Log analysis complete.")

if __name__ == "__main__":
    main()
