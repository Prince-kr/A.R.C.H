import argparse
import time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--payload", default="")
    args = parser.parse_args()

    print(f"[*] Starting DoS attack simulation on {args.target}...")
    time.sleep(2)
    print(f"[+] Flooding {args.target} with ICMP packets...")
    print(f"[!] SYN flood triggered. Target response time increasing.")
    print("[*] Attack finished.")

if __name__ == "__main__":
    main()
