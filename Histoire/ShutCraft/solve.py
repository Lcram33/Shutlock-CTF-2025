import json
import re
import string


# Path to the dataset (obtained here : https://mcasset.cloud/1.16.4/assets/minecraft/lang/en_us.json)
EN_US_PATH = "en_us.json"

# You should not edit this
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

# Our encoded mail
XOR_STR = "\r\u0018\u001b\fFX\u0002\u0007C\u0016\u0002\u001e\n\u0007\u0012O\u00112\u0018\u0019\u001aJ8\n\u0016]\u0005\r\u001a\u0015\u000b\u000f\u000e\u0000\u0016\u0019I"


def decode_mail(encoded, key):
    if len(key) < len(encoded):
        extend = (len(encoded) - len(key)) // len(key) + 2
        key *= extend

    encoded_bytes = encoded.encode('latin1') # Yes, this line can be confusing
                                             # but encoded mail is a string !
    key_bytes = key.encode('latin1')
    
    decoded = bytearray()
    for i in range(len(encoded_bytes)):
        decoded.append(encoded_bytes[i] ^ key_bytes[i])

    return bytes(decoded)

def is_printable_ascii(s):
    return all(c in string.printable for c in s)

def is_valid_email(s):
    return EMAIL_REGEX.fullmatch(s.strip())

def get_block_keys_from_json(path):
    # Read file and filter block.minecraft.* entries
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [k for k in data if k.startswith("block.minecraft.")]

def bruteforce_key(keys):
    found = []
    for key in keys:
        attempt = decode_mail(XOR_STR, key)
        try:
            decoded_str = attempt.decode("utf-8")
            if is_printable_ascii(decoded_str) and is_valid_email(decoded_str):
                found.append((key, decoded_str))
        except UnicodeDecodeError:
            continue
    
    return found


# Main program
def main():
    wordlist = get_block_keys_from_json(EN_US_PATH)
    print(f"[i] {len(wordlist)} keys loaded. Starting bruteforce...")
    results = bruteforce_key(wordlist)

    if results:
        print("[!] Email(s) found :")
        for key, email in results:
            flag = "SHLK{" + email + "}"
            print(f"    [i] Key : {key}")
            print(f"    [i] Email : {email}")
            print(f"    [i] Flag : {flag}")
            print()
    else:
        print("[X] No email found.")

if __name__ == "__main__":
    main()
