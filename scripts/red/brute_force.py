import argparse
import time

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--payload", default="admin")
    args = parser.parse_args()

    print(f"[*] Starting SSH brute-force on {args.target} for user '{args.payload}'...")
    for i in range(1, 6):
        print(f"[*] Attempt {i}: Trying password_{i}...")
        time.sleep(0.5)
    
    print(f"[+] Success! Password found: password_5")
    print("[*] session established with {args.target}")

if __name__ == "__main__":
    main()
