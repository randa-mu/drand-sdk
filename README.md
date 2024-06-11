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
