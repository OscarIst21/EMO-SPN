
# EMO-SPN
import os, sys, argparse, hashlib, struct, time

SANDBOX_DIR = os.path.abspath("sandbox")
ESCROW_DIR = os.path.abspath("escrow")
R = 32  # rounds
BLOCK_SIZE = 16  # bytes (128 bits)
MASTER_KEY_SIZE = 32  # bytes (256 bits)
s
def ensure_dirs():
    os.makedirs(SANDBOX_DIR, exist_ok=True)
    os.makedirs(ESCROW_DIR, exist_ok=True)

def sandbox_path_ok(path):
    ap = os.path.abspath(path)
    return ap.startswith(SANDBOX_DIR + os.sep) or ap == SANDBOX_DIR

def abort_if_not_in_sandbox(path):
    if not sandbox_path_ok(path):
        raise PermissionError(f"Operation aborted: path {path} is outside sandbox/")

class XORShift64:
    def __init__(self, seed_bytes):
        h = hashlib.sha256(seed_bytes).digest()
        self.state = int.from_bytes(h[:8], 'big') or 0xdeadbeefcafebabe
    def next64(self):
        x = self.state & ((1<<64)-1)
        x ^= (x << 13) & ((1<<64)-1)
        x ^= (x >> 7)
        x ^= (x << 17) & ((1<<64)-1)
        self.state = x & ((1<<64)-1)
        return self.state
    def randbytes(self, n):
        out = bytearray()
        while len(out) < n:
            v = self.next64()
            out += v.to_bytes(8, 'big')
        return bytes(out[:n])

def sbox_gen(master_key):
    prng = XORShift64(master_key + b"SBOX")
    arr = list(range(256))
    for i in range(255, 0, -1):
        r = int.from_bytes(prng.next64().to_bytes(8,'big')[:8], 'big') % (i+1)
        arr[i], arr[r] = arr[r], arr[i]
    sbox = bytes(arr)
    inv = [0]*256
    for i,v in enumerate(sbox):
        inv[v] = i
    return sbox, bytes(inv)

def player_gen(master_key):
    prng = XORShift64(master_key + b"PLAYER")
    arr = list(range(128))
    for i in range(127, 0, -1):
        r = int.from_bytes(prng.next64().to_bytes(8,'big')[:8], 'big') % (i+1)
        arr[i], arr[r] = arr[r], arr[i]
    inv = [0]*128
    for i,v in enumerate(arr):
        inv[v] = i
    return arr, inv

def apply_player(block_bytes, perm):
    bits = []
    for b in block_bytes:
        for i in range(8):
            bits.append((b >> (7-i)) & 1)
    outbits = [0]*128
    for i in range(128):
        outbits[i] = bits[perm[i]]
    out = bytearray(16)
    for i in range(16):
        val = 0
        for j in range(8):
            val = (val << 1) | outbits[i*8 + j]
        out[i] = val
    return bytes(out)

def key_schedule(master_key):
    prng = XORShift64(master_key + b"KS")
    keys = []
    for _ in range(R+1):
        keys.append(prng.randbytes(16))
    return keys

def sub_bytes(block_bytes, sbox):
    return bytes(sbox[b] for b in block_bytes)

def sub_bytes_inv(block_bytes, inv_sbox):
    return bytes(inv_sbox[b] for b in block_bytes)

def xor_bytes(a,b):
    return bytes(x^y for x,y in zip(a,b))

def pkcs7_pad(data):
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len])*pad_len

def pkcs7_unpad(data):
    if len(data)==0 or len(data)%BLOCK_SIZE!=0:
        raise ValueError("Invalid padding length")
    pad = data[-1]
    if pad<1 or pad>BLOCK_SIZE:
        raise ValueError("Invalid padding value")
    if data[-pad:] != bytes([pad])*pad:
        raise ValueError("Invalid padding bytes")
    return data[:-pad]

def encrypt_block(block, keys, sbox, player):
    x = xor_bytes(block, keys[0])
    for r in range(1, R+1):
        x = sub_bytes(x, sbox)
        x = apply_player(x, player)
        x = xor_bytes(x, keys[r])
    return x

def decrypt_block(block, keys, inv_sbox, inv_player):
    x = block
    for r in range(R, 0, -1):
        x = xor_bytes(x, keys[r])
        x = apply_player(x, inv_player)
        x = sub_bytes_inv(x, inv_sbox)
    x = xor_bytes(x, keys[0])
    return x

def hmac_sha256(key, data):
    block_size = 64
    if len(key) > block_size:
        key = hashlib.sha256(key).digest()
    key = key.ljust(block_size, b'\x00')
    o_key = bytes((b ^ 0x5c) for b in key)
    i_key = bytes((b ^ 0x36) for b in key)
    return hashlib.sha256(o_key + hashlib.sha256(i_key + data).digest()).digest()

def create_escrow(master_key, passphrase, outpath):
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, 200000, dklen=32)
    blob = bytes(a^b for a,b in zip(master_key, dk))
    mac = hmac_sha256(dk, salt+blob)
    with open(outpath, "wb") as f:
        f.write(salt + blob + mac)

def recover_from_escrow(passphrase, inpath):
    with open(inpath, "rb") as f:
        data = f.read()
    salt = data[:16]
    blob = data[16:16+MASTER_KEY_SIZE]
    mac = data[16+MASTER_KEY_SIZE:]
    dk = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, 200000, dklen=32)
    if hmac_sha256(dk, salt+blob) != mac:
        raise ValueError("Escrow MAC mismatch or wrong passphrase")
    master_key = bytes(a^b for a,b in zip(blob, dk))
    return master_key

def encrypt_file(infile, outfile, master_key):
    abort_if_not_in_sandbox(outfile)
    sbox, inv_sbox = sbox_gen(master_key)
    player, inv_player = player_gen(master_key)
    keys = key_schedule(master_key)
    iv = os.urandom(16)
    with open(infile, "rb") as f:
        data = f.read()
    padded = pkcs7_pad(data)
    ciphertext = bytearray()
    prev = iv
    for i in range(0, len(padded), BLOCK_SIZE):
        block = padded[i:i+BLOCK_SIZE]
        block = xor_bytes(block, prev)
        c = encrypt_block(block, keys, sbox, player)
        ciphertext += c
        prev = c
    tag = hmac_sha256(master_key, iv + ciphertext)
    with open(outfile, "wb") as f:
        f.write(iv + ciphertext + tag)

def decrypt_file(infile, outfile, master_key):
    abort_if_not_in_sandbox(outfile)
    with open(infile, "rb") as f:
        data = f.read()
    if len(data) < 16 + 32:
        raise ValueError("Ciphertext too short")
    iv = data[:16]
    tag = data[-32:]
    ciphertext = data[16:-32]
    if hmac_sha256(master_key, iv + ciphertext) != tag:
        raise ValueError("MAC verification failed")
    sbox, inv_sbox = sbox_gen(master_key)
    player, inv_player = player_gen(master_key)
    keys = key_schedule(master_key)
    plaintext_padded = bytearray()
    prev = iv
    for i in range(0, len(ciphertext), BLOCK_SIZE):
        c = ciphertext[i:i+BLOCK_SIZE]
        block = decrypt_block(c, keys, inv_sbox, inv_player)
        block = xor_bytes(block, prev)
        plaintext_padded += block
        prev = c
    plaintext = pkcs7_unpad(bytes(plaintext_padded))
    with open(outfile, "wb") as f:
        f.write(plaintext)

def test_basic_flow():
    print("Running basic flow test...")
    master_key = os.urandom(MASTER_KEY_SIZE)
    ensure_dirs()
    sample = b"Hola Mundo EMO-SPN"
    infile = os.path.join(SANDBOX_DIR, "sample.txt")
    enc = os.path.join(SANDBOX_DIR, "sample.enc")
    dec = os.path.join(SANDBOX_DIR, "sample.dec.txt")
    with open(infile, "wb") as f:
        f.write(sample)
    encrypt_file(infile, enc, master_key)
    decrypt_file(enc, dec, master_key)
    with open(dec, "rb") as f:
        out = f.read()
    print("Original:", sample)
    print("Decrypted:", out)
    assert sample == out
    print("Basic flow OK")

def test_avalanche(n=100):
    print("Running avalanche sample with", n, "pairs...")
    master_key = os.urandom(MASTER_KEY_SIZE)
    sbox, inv = sbox_gen(master_key)
    player, inv_player = player_gen(master_key)
    keys = key_schedule(master_key)
    diffs = []
    for i in range(n):
        pt = os.urandom(BLOCK_SIZE)
        b = bytearray(pt)
        b[i % BLOCK_SIZE] ^= 1 << (i % 8)
        pt2 = bytes(b)
        c1 = encrypt_block(pt, keys, sbox, player)
        c2 = encrypt_block(pt2, keys, sbox, player)
        x = int.from_bytes(c1, 'big') ^ int.from_bytes(c2, 'big')
        diff = bin(x).count("1")
        diffs.append(diff)
    avg = sum(diffs)/len(diffs)
    print("Average differing bits (per block):", avg)
    print("Sample diffs (first 10):", diffs[:10])

def cmd_init(args):
    ensure_dirs()
    master_key = os.urandom(MASTER_KEY_SIZE)
    passphrase = args.passphrase or input("Escrow passphrase: ")
    escrow_path = os.path.join(ESCROW_DIR, "recovery.enc")
    create_escrow(master_key, passphrase, escrow_path)
    keyfile = os.path.join(SANDBOX_DIR, "key.bin.enc")
    create_escrow(master_key, passphrase, keyfile)
    print("Init complete.")
    print("Escrow at:", escrow_path)
    print("Encrypted key in sandbox at:", keyfile)

def cmd_encrypt(args):
    ensure_dirs()
    infile = args.infile
    outfile = args.outfile
    if not infile or not outfile:
        print("Provide infile and outfile")
        return
    abort_if_not_in_sandbox(infile)
    abort_if_not_in_sandbox(outfile)
    if args.escrow:
        passphrase = args.passphrase or input("Escrow passphrase: ")
        master_key = recover_from_escrow(passphrase, args.escrow)
    else:
        keyfile = os.path.join(SANDBOX_DIR, "key.bin.enc")
        if not os.path.exists(keyfile):
            raise FileNotFoundError("No key found; run init or provide --escrow")
        passphrase = args.passphrase or input("Sandbox key passphrase: ")
        master_key = recover_from_escrow(passphrase, keyfile)
    encrypt_file(infile, outfile, master_key)
    print("Encrypted", infile, "->", outfile)

def cmd_decrypt(args):
    ensure_dirs()
    infile = args.infile
    outfile = args.outfile
    if not infile or not outfile:
        print("Provide infile and outfile")
        return
    abort_if_not_in_sandbox(infile)
    abort_if_not_in_sandbox(outfile)
    if args.escrow:
        passphrase = args.passphrase or input("Escrow passphrase: ")
        master_key = recover_from_escrow(passphrase, args.escrow)
    else:
        keyfile = os.path.join(SANDBOX_DIR, "key.bin.enc")
        if not os.path.exists(keyfile):
            raise FileNotFoundError("No key found; run init or provide --escrow")
        passphrase = args.passphrase or input("Sandbox key passphrase: ")
        master_key = recover_from_escrow(passphrase, keyfile)
    decrypt_file(infile, outfile, master_key)
    print("Decrypted", infile, "->", outfile)

def cmd_test(args):
    ensure_dirs()
    test_basic_flow()
    test_avalanche(n=200)

def main():
    parser = argparse.ArgumentParser(prog="emo_spn")
    sub = parser.add_subparsers(dest="cmd")
    p_init = sub.add_parser("init")
    p_init.add_argument("--passphrase", "-p", help="passphrase for escrow")
    p_enc = sub.add_parser("encrypt")
    p_enc.add_argument("infile")
    p_enc.add_argument("outfile")
    p_enc.add_argument("--escrow", help="path to escrow file (default: escrow/recovery.enc)",
                       default=os.path.join(ESCROW_DIR, "recovery.enc"))
    p_enc.add_argument("--passphrase", "-p", help="passphrase to unlock escrow/key")
    p_dec = sub.add_parser("decrypt")
    p_dec.add_argument("infile")
    p_dec.add_argument("outfile")
    p_dec.add_argument("--escrow", help="path to escrow file (default: escrow/recovery.enc)",
                       default=os.path.join(ESCROW_DIR, "recovery.enc"))
    p_dec.add_argument("--passphrase", "-p", help="passphrase to unlock escrow/key")
    p_test = sub.add_parser("test")
    args = parser.parse_args()
    try:
        if args.cmd == "init":
            cmd_init(args)
        elif args.cmd == "encrypt":
            cmd_encrypt(args)
        elif args.cmd == "decrypt":
            cmd_decrypt(args)
        elif args.cmd == "test":
            cmd_test(args)
        else:
            parser.print_help()
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()

# ============================================================
# FUNCIONES PÚBLICAS PARA USAR EL CIFRADOR PROGRAMÁTICAMENTE
# ============================================================
# ============================================================
# FUNCIONES PÚBLICAS PARA USAR EL CIFRADOR PROGRAMÁTICAMENTE
# - Devuelven (resultado_bytes, elapsed_seconds)
# - Formato de salida: IV(16) || C || TAG(32)
# ============================================================

def emo_encrypt(message: str, key: str):
    """
    Cifra un mensaje (string) y devuelve (cipher_bytes, elapsed_seconds).
    El formato del resultado es: IV || C || TAG (HMAC-SHA256 with master key).
    """
    from hashlib import sha256
    t0 = time.perf_counter()

    # Derivar clave maestra de 256 bits desde la passphrase/key
    master_key = sha256(key.encode()).digest()  # 32 bytes

    # Generar S-box, P-layer y subclaves
    sbox, inv_sbox = sbox_gen(master_key)
    player, inv_player = player_gen(master_key)
    keys = key_schedule(master_key)

    # Preparar datos (padding PKCS7)
    data = message.encode()
    padded = pkcs7_pad(data)

    # CBC-like: IV random
    iv = os.urandom(16)
    prev = iv
    ciphertext = bytearray()

    for i in range(0, len(padded), BLOCK_SIZE):
        block = padded[i:i+BLOCK_SIZE]
        block = xor_bytes(block, prev)
        c = encrypt_block(block, keys, sbox, player)
        ciphertext += c
        prev = c

    tag = hmac_sha256(master_key, iv + ciphertext)
    out = bytes(iv + ciphertext + tag)

    t1 = time.perf_counter()
    return out, (t1 - t0)


def emo_decrypt(cipher_bytes: bytes, key: str):
    """
    Descifra bytes (en formato IV||C||TAG) y devuelve (plaintext_str, elapsed_seconds).
    Lanza ValueError si MAC inválida o padding incorrecto.
    """
    from hashlib import sha256
    t0 = time.perf_counter()

    if len(cipher_bytes) < 16 + 32:
        raise ValueError("Ciphertext demasiado corto")

    master_key = sha256(key.encode()).digest()

    iv = cipher_bytes[:16]
    tag = cipher_bytes[-32:]
    ciphertext = cipher_bytes[16:-32]

    # Verificar MAC
    if hmac_sha256(master_key, iv + ciphertext) != tag:
        raise ValueError("MAC verification failed")

    # Regenerar S-box, P-layer y subclaves
    sbox, inv_sbox = sbox_gen(master_key)
    player, inv_player = player_gen(master_key)
    keys = key_schedule(master_key)

    prev = iv
    plaintext_padded = bytearray()

    for i in range(0, len(ciphertext), BLOCK_SIZE):
        c = ciphertext[i:i+BLOCK_SIZE]
        block = decrypt_block(c, keys, inv_sbox, inv_player)
        block = xor_bytes(block, prev)
        plaintext_padded += block
        prev = c

    plaintext = pkcs7_unpad(bytes(plaintext_padded))
    t1 = time.perf_counter()
    return plaintext.decode(errors="replace"), (t1 - t0)
