#!/bin/python3
# Usage: python3 kat_beacon_extender.py --language rust

import argparse
import math
import textwrap
from Crypto.Hash import keccak
from Crypto.Hash import SHAKE128
from Crypto.Util.strxor import strxor

# Reference implementation used to expand a randomness beacon using a fixed-output hash function
def expand_beacon_fixedhash(hasher, randomness_beacon, DST, len_in_bytes):
    def H(m):
        h = hasher.new()
        h.update(m)
        return h.digest()

    def I2OSP(v, len):
        return int(v).to_bytes(len, "big")

    b_in_bytes = hasher.digest_size
    ell = math.ceil(len_in_bytes / b_in_bytes)
    if ell > 2**16 or len(DST) > 255:
        raise ValueError("Invalid args")

    DST_prime = DST + I2OSP(len(DST), 1)
    msg_prime = randomness_beacon + I2OSP(0, 2) + DST_prime

    b = []
    b.append(H(msg_prime))
    b.append(H(b[0] + I2OSP(1, 2) + DST_prime))

    for i in range(2, ell + 1):
        b.append(H(strxor(b[0], b[-1]) + I2OSP(i, 2) + DST_prime))

    uniform_bytes = b"".join(b[1:])
    return uniform_bytes[:len_in_bytes]


# Reference implementation used to expand a randomness beacon using a extensible-output hash function
def expand_beacon_xof(hasher, randomness_beacon, DST, len_in_bytes):
    def I2OSP(v, len):
        return int(v).to_bytes(len, "big")

    if len(DST) > 255:
        raise ValueError("Invalid args")

    DST_prime = DST + I2OSP(len(DST), 1)
    msg_prime = randomness_beacon + DST_prime
    h = hasher.new(msg_prime)
    return h.read(len_in_bytes)

# Keccak-256, SHAKE128
hash_functions = [
    {
        "hash_name": b"Keccak-256",
        "hasher": keccak.new(digest_bits=256),
        "expand_fn": expand_beacon_fixedhash,
    },
    {
        "hash_name": b"SHAKE128",
        "hasher": SHAKE128.new(),
        "expand_fn": expand_beacon_xof,
    },
]

def print_kats(language):
    for hash_fn in hash_functions:
        expand_fn_name = (
            b"-with-xof" if hash_fn["expand_fn"] == expand_beacon_xof else b""
        )
        DST = b"BeaconExtenderKAT-v01" + expand_fn_name + b"-" + hash_fn["hash_name"]
        kat_inputs = [
            {
                "randomness_beacon": bytes.fromhex(
                    "0000000000000000000000000000000000000000000000000000000000000000"
                ),
                "DST": DST,
                "length": 32,
            },
            {
                "randomness_beacon": bytes.fromhex(
                    "0a0b0c0d0e0f000102030405060708090A0B0C0D0E0F00010203040506070809"
                ),
                "DST": DST,
                "length": 1,
            },
            {
                "randomness_beacon": bytes.fromhex(
                    "0A0a000A0a010A0a020A0a030A0a040A0a050A0a060A0a070A0a080A0a090A0b"
                ),
                "DST": DST,
                "length": 4,
            },
            {
                "randomness_beacon": bytes.fromhex(
                    "c5511916c97b90660eee5bd2e678899cd6946cdd5404d235a127067bfbd4758f"
                ),
                "DST": DST,
                "length": 32,
            },
            {
                "randomness_beacon": bytes.fromhex(
                    "8876517e60e0a79c4c3ef2877df1f19a6a76aff3550c19a9e9e088a41f813b14"
                ),
                "DST": DST,
                "length": 64,
            },
            {
                "randomness_beacon": bytes.fromhex(
                    "b2308b0969926631e0d74053ff20b8d167eed55b21803f4d85475b838aee8a54"
                ),
                "DST": DST,
                "length": 68,
            },
        ]

        print("-----------------------------------------------------------")
        print(hash_fn["hash_name"].decode())
        print(f"DST = {DST.decode()}")
        print(f'hash = {hash_fn["hash_name"].decode()}')
        print()

        # if language == "rust"
        for inp in kat_inputs:
            expand_fn, hasher = hash_fn["expand_fn"], hash_fn["hasher"]
            beacon, DST, len_in_bytes = (
                inp["randomness_beacon"],
                inp["DST"],
                inp["length"],
            )

            out = expand_fn(hasher, beacon, DST, len_in_bytes)

            if language == "txt":
                print(f"randomness_beacon = {beacon.hex()}")
                print(f"len_in_bytes      = {len_in_bytes}")
                print(f"uniform_bytes     = {out.hex()}")
                print()
            elif language == "rust":
                kat = f"""\
                #[case(
                    &hex!("{beacon.hex()}"),
                    b"{DST.decode()}",
                    &hex!("{out.hex()}"),
                )]"""
                print(textwrap.dedent(kat))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="beacon_extender_kat")
    parser.add_argument(
        "--language", required=False, choices=["txt", "rust"], default="txt"
    )
    args = parser.parse_args()

    print_kats(args.language)
