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

(I'm not too sure about type signatures here)
```
// Uint32 returns a pseudo-random 32-bit value as a uint32.
Uint32() uint32
// Uint64 returns a pseudo-random 64-bit value as a uint64.
Uint64() uint64

// Int31 returns a non-negative pseudo-random 31-bit integer as an int32.
Int31() int32
// Int63 returns a non-negative pseudo-random 63-bit integer as an int64.
Int63() int64

// Uintn returns, as an uint, a pseudo-random number in the half-open interval [0,n). It panics if n <= 0.
Uintn(max uint) uint


Range(min, max big.Int) big.Int
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
