# SDK for drand usage

This repo documents the APIs available to use verifiable randomness from the drand network effectively in your projects.

Goals for this repo are to:
 - Provide clear derivation paths and algorithm for random values of different types.
 - Provide the necessary "verification algorithms" for said derivation paths.
 - Provide a clear set of APIs that allow users to use verifiable randomness in their code without having to care about it.


# Developer needs satisfied by our APIs

The following usecases are the ones we have designed the drand VRF SDK for.
If you have a specific usecase for randomness that you feel

## Pick a random integer using drand VRF

## Pick a random double using drand VRF

This is not a supported feature: picking a random double is something you should usually avoid doing because of the machine precision that doesn't allow for properly uniformly distributed doubles.

## Pick an element in a set of elements using drand VRF

## Shuffle an array using drand VRF



## Get a random bytestring using drand VRF
