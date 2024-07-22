# SDK for drand usage

This repo documents the APIs available to use verifiable randomness from the drand network effectively in your projects.

Goals for this repo are to:
 - Provide clear derivation paths and algorithm for random values of different types.
 - Provide the necessary "verification algorithms" for said derivation paths.
 - Provide a clear set of APIs that allow users to use verifiable randomness in their code without having to care about it.


# Developer needs satisfied by our APIs

The following usecases are the ones we have designed the drand VRF SDK for.
If you have a specific usecase for randomness that you feel is missing here, please reach out to us.

## Pick a random integer using drand VRF

```
// Integer functions have the following syntax
// v1 := int_rng.NextUint32()
// v2 := int_rng.NextUint32() // v2 != v1
// int_ver.Uint32([...]uint32{v1, v2}) // nil
// int_ver.Uint32([...]uint32{v2, v1}) // error

// IntRng::NextUint32 returns a pseudo-random 32-bit value as a uint32.
(int_rng IntRng) NextUint32() uint32

// IntRng::NextUint64 returns a pseudo-random 64-bit value as a uint64.
(int_rng IntRng) NextUint64() uint64

// IntRng::NextInt31 returns a non-negative pseudo-random 31-bit integer as an int32.
(int_rng IntRng) NextInt31() int32

// IntRng::NextInt63 returns a non-negative pseudo-random 63-bit integer as an int64.
(int_rng IntRng) NextInt63() int64

// IntVer::Uint32 verifies that an array of sequential Uint32 is valid.
(int_ver IntVer) Uint32([]uint32) error

// IntVer::Uint64 verifies that an array of sequential Uint64 is valid.
(int_ver IntVer) Uint64([]uint64) error

// IntVer::Int31 verifies that an array of sequential Int31 is valid.
(int_ver IntVer) Int31([]int32) error

// Structure used to generate numbers within an interval
type IntnRng struct {
    n uint
    ...
}

// Structure used to generate numbers within a range
type RangeRng struct {
    min, max big.Int
    ...
}

// UintnRng::Uintn returns, as an uint, a pseudo-random number in the half-open interval [0,n) defined in UintnRng
(uintn_rng UintnRng) NextUintn() uint

// UintnVer::Uintn verifies that an array of sequential Uintn is valid.
(uintn_ver UintnVer) Uintn([]uint) error

// RangeRng::NextRange returns, as a big.Int, a pseudo-random number in the half-open interval [min,max) defined in RangeRng
(range_rng RangeRng) NextRange() big.Int
```
(Do we need int8, int16 and their uint counterparts? Do we need a literally generic function taking the expected bit size?)

## Pick a random double using drand VRF

This is not a supported feature: picking a random double is something you should usually avoid doing because of the machine precision that doesn't allow for properly uniformly distributed doubles.

## Pick an element in a set of elements using drand VRF

TBD: which picking algorithm do we want to use? Just `A[Uintn(len(A))]`?

```
// Pick selects one element at random in the array A and return it and its index.
Pick(A []any) (index int, element any)

// PickN selects N elements in the array A and returns an array of their indices and a new array containing them.
PickN(A []any, N uint32) (indices [N]int, elements [N]any)
```


## Shuffle an array using drand VRF

TBD: which shuffle algorithm do we want to use? Knuth?

```
// Shuffle pseudo-randomizes the order of the elements of the input A.
Shuffle(A []any) []any
```


## Get a random bytestring using drand VRF

The drand beacons are always made of 2 things: a round number and a signature.
The signature is a indistinguishable from a random element in the space of all possible signatures, however this is not the same as being a random bytestring.
The possible signatures are constrained by the underlying elliptic curves used to produce them, therefore the signatures have an agebraic structure that we need to get rid of first in order to get a random bytestring.
The easiest way of getting rid of that algebraic structure is to process the beacon's signature through either a hash function or an extensible output function (XOF).
The signature scheme used to produce drand signatures is operating on 255-bit prime order subgroups.

```
// Read generates n random bytes using Blake2X as its XOF and an optional seed.
Read(n uint32, seed []byte) [n]byte

// Sha256() returns the SHA-256 hash of the drand signature. Note this is the "default" way of getting bytes out of a drand beacon.
Sha256() []byte

```

# Technical background
We design the SDK based on three key requirements: 
 1. Ability to generate more random bits than the randomness beacon
 1. Each SDK function must have an independent output
 1. Developers should have the ability to derive application specific values from the randomness beacon

We solve (1) by relying on a variable-length keyed hash function. By providing the randomness beacon as a key/seed to a hash function, we can deterministically derive more bits. This allows us to provide functions that output far more than 256 random bits.

To solve (2) and (3), we opt for a Domain Separation Tag (DST). A DST is a *static public* value, known to both the generator and the verifier. By including it in addition to the seed and with a different value in each derivation function, this guarantees (2). Solving (3) requires the developer to specify his own value; we name this parameter AppName.

We build the DST as follows: `<AppName>-v<SdkVersion>-<FnName>` where 
 - `<AppName>` is the application name provided by the developer. Defaults to `drand`.
 - `<SdkVersion>` is the current version of the SDK.
 - `<FnName>` is the name of the SDK function being used.

Each SDK function works by generating a random byte string based on the `expand_message_xmd` and `expand_message_xof` functions described in [rfc9380](https://datatracker.ietf.org/doc/html/rfc9380#name-expand_message_xmd). 

For non-extensible hash function such as `SHA-3`, `Keccak-256`, we use the following algorithm based on `expand_message_xmd`:
```
Parameters:
H(m), a fixed-length hash function such as SHA-3/Keccak-256 (Merkle-Damgard not supported).
b_in_bytes, the output size of H in bytes.

Input:
- randomness_beacon, a 32 bytes string corresponding to the randomness beacon.
- DST, a byte string of at most 255 bytes used for domain separation.
- len_in_bytes, the length of the requested output in bytes.

1.  ell = ceil(len_in_bytes / b_in_bytes)
2.  ABORT if ell > 2^16 or len(DST) > 255
3.  DST_prime = DST || I2OSP(len(DST), 1)
4.  msg_prime = randomness_beacon || I2OSP(0, 2) || DST_prime
5.  b_0 = H(msg_prime)
6.  b_1 = H(b_0 || I2OSP(1, 2) || DST_prime)
7.  for i in (2, ..., ell):
8.     b_i = H(strxor(b_0, b_(i - 1)) || I2OSP(i, 2) || DST_prime)
9.  uniform_bytes = b_1 || ... || b_ell
10. return substr(uniform_bytes, 0, len_in_bytes)
```

For XOF such as `SHAKE128`, `BLAKE2X` we use the following algorithm: 
```
Parameters:
H(m, len), a variable-length hash function such as SHAKE128/BLAKE2X.

Input:
- randomness_beacon, a 32 bytes string corresponding to the randomness beacon.
- DST, a byte string of at most 255 bytes used for domain separation.
- len_in_bytes, the length of the requested output in bytes.

1. ABORT if len(DST) > 255
2. DST_prime = DST || I2OSP(len(DST), 1)
3. msg_prime = randomness_beacon || DST_prime
4. uniform_bytes = H(msg_prime, len_in_bytes)
```


# Test Vectors

## Expand Beacon - Fixed Output Hash

### Keccak-256
```text
DST = BeaconExtenderKAT-v01-Keccak-256
hash = Keccak-256

randomness_beacon = 0000000000000000000000000000000000000000000000000000000000000000
len_in_bytes      = 32
uniform_bytes     = ed8597daf957b84627c40c8c0a7b37a57332e71de230cb997bc2d953a4578329

randomness_beacon = 0a0b0c0d0e0f000102030405060708090a0b0c0d0e0f00010203040506070809
len_in_bytes      = 1
uniform_bytes     = c5

randomness_beacon = 0a0a000a0a010a0a020a0a030a0a040a0a050a0a060a0a070a0a080a0a090a0b
len_in_bytes      = 4
uniform_bytes     = f0c2c6c6

randomness_beacon = c5511916c97b90660eee5bd2e678899cd6946cdd5404d235a127067bfbd4758f
len_in_bytes      = 32
uniform_bytes     = 2d3382e2130624bcd615a033da8af220470bcce7faed24cc40933cdb77e96f8b

randomness_beacon = 8876517e60e0a79c4c3ef2877df1f19a6a76aff3550c19a9e9e088a41f813b14
len_in_bytes      = 64
uniform_bytes     = 23d8f39354e31ba07e8f6eb9820ef8fab7ed11dc0fae2568f5d661f86127dad9a66afa00d76e5dca633d3149ce5eed9d9f5a21dc26e1c79ee9a71c14b75ad175

randomness_beacon = b2308b0969926631e0d74053ff20b8d167eed55b21803f4d85475b838aee8a54
len_in_bytes      = 68
uniform_bytes     = 0c09746a3bde39a0992138f3715601cbda6a54b516c50982da0e8fb5e915bc3b3d7d610b08f20503bc18fdc2495ca1bc6d104a8b1d85c8089d1c88c763710060a9577624
```

## Expand Beacon - Extensible Hash
### Shake128
```text
DST = BeaconExtenderKAT-v01-XofSHAKE128
hash = SHAKE128

randomness_beacon = 0000000000000000000000000000000000000000000000000000000000000000
len_in_bytes      = 32
uniform_bytes     = 421395f0db433569f8393fd3e2255b9dbaafa67bbe5441e6bc1601ff059d4aa7

randomness_beacon = 0a0b0c0d0e0f000102030405060708090a0b0c0d0e0f00010203040506070809
len_in_bytes      = 1
uniform_bytes     = e9

randomness_beacon = 0a0a000a0a010a0a020a0a030a0a040a0a050a0a060a0a070a0a080a0a090a0b
len_in_bytes      = 4
uniform_bytes     = a1e606fe

randomness_beacon = c5511916c97b90660eee5bd2e678899cd6946cdd5404d235a127067bfbd4758f
len_in_bytes      = 32
uniform_bytes     = 35f3a3ac0dbd26f051578c22ab68304ffa98cd199d68ecbfe7f2de0e94816fef

randomness_beacon = 8876517e60e0a79c4c3ef2877df1f19a6a76aff3550c19a9e9e088a41f813b14
len_in_bytes      = 64
uniform_bytes     = c765f1efc4e3623a4f847db39edc8286b7b0db2ed6cf196cb5ea71345359799997f01cec05036303310aec3a61318bc4eb34711508ddb56621623a6f64702660

randomness_beacon = b2308b0969926631e0d74053ff20b8d167eed55b21803f4d85475b838aee8a54
len_in_bytes      = 68
uniform_bytes     = a5ebddb90cb0c8bd1661de820f6e79191d67f57158e521204add5ced8d17f3e30ce7decf43dd18cfa3740017605a8abb12ff9023e0d1dfab42b7c723aacdc8ad47bb53f9
```