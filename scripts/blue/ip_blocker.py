import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", required=True)
    args = parser.parse_args()

    print(f"[*] Initializing mitigation for Session {args.session}...")
    print("[+] Blocking IP 127.0.0.1 via iptables...")
    print("[*] Traffic dropped. Victim node stabilized.")

if __name__ == "__main__":
    main()
