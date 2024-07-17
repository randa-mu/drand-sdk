# drand REST API

## Overview
The `drand` REST API provides endpoints to retrieve cryptographically secure random values derived from the latest randomness beacon. The API supports various operations, including fetching company-specific information and generating random numbers of different sizes.

## API Endpoints

<details>
 <summary><code>GET</code> <code><b>/{company}</b></code> <code>(Returns the Domain Separation Tag and other information required to verify random values)</code></summary>

##### Parameters

- `company` (path parameter, required): Name of the company.

##### Responses

> | http code     | content-type                      | response                                  |
> |---------------|-----------------------------------|-------------------------------------------|
> | `200`         | `application/json`                | CompanyResponse                           |
> | `404`         | `application/json`                | Company does not exist                    |

##### Example cURL

> ```bash
> curl -X GET "http://localhost:8889/exampleCompany" -H "Authorization: Bearer <your_jwt_token>"
> ```

##### Sample Output
```json
{
  "dst": "exampleDomainSeparationTag"
}
```

</details>

<details>
 <summary><code>POST</code> <code><b>/{company}/latest/uint32</b></code> <code>(Returns a uint32 derived from the latest randomness beacon)</code></summary>

##### Parameters

- `company` (path parameter, required): Name of the company.

##### Request Body

> | content-type     | schema                            |
> |------------------|-----------------------------------|
> | `application/json`| RandomnessRequest                |

##### Responses

> | http code     | content-type                      | response                                  |
> |---------------|-----------------------------------|-------------------------------------------|
> | `200`         | `application/json`                | RandomnessResponse                        |
> | `401`         | `application/json`                | Unauthorized                              |
> | `404`         | `application/json`                | Company does not exist                    |

##### Example cURL

> ```bash
> curl -X POST "http://localhost:8889/exampleCompany/latest/uint32" -H "Authorization: Bearer <your_jwt_token>" -H "Content-Type: application/json" -d '{"seed": "abcdef1234567890"}'
> ```

##### Sample Output
```json
{
  "round": 12345,
  "randomness": "1a2b3c4d5e6f7890"
}
```

</details>

<details>
 <summary><code>POST</code> <code><b>/{company}/latest/uint64</b></code> <code>(Returns a uint64 derived from the latest randomness beacon)</code></summary>

##### Parameters

- `company` (path parameter, required): Name of the company.

##### Request Body

> | content-type     | schema                            |
> |------------------|-----------------------------------|
> | `application/json`| RandomnessRequest                |

##### Responses

> | http code     | content-type                      | response                                  |
> |---------------|-----------------------------------|-------------------------------------------|
> | `200`         | `application/json`                | RandomnessResponse                        |
> | `401`         | `application/json`                | Unauthorized                              |
> | `404`         | `application/json`                | Company does not exist                    |

##### Example cURL

> ```bash
> curl -X POST "http://localhost:8889/exampleCompany/latest/uint64" -H "Authorization: Bearer <your_jwt_token>" -H "Content-Type: application/json" -d '{"seed": "abcdef1234567890"}'
> ```

##### Sample Output
```json
{
  "round": 12345,
  "randomness": "2b3c4d5e6f789012"
}
```

</details>

<details>
 <summary><code>POST</code> <code><b>/{company}/latest/uint128</b></code> <code>(Returns a uint128 derived from the latest randomness beacon)</code></summary>

##### Parameters

- `company` (path parameter, required): Name of the company.

##### Request Body

> | content-type     | schema                            |
> |------------------|-----------------------------------|
> | `application/json`| RandomnessRequest                |

##### Responses

> | http code     | content-type                      | response                                  |
> |---------------|-----------------------------------|-------------------------------------------|
> | `200`         | `application/json`                | RandomnessResponse                        |
> | `401`         | `application/json`                | Unauthorized                              |
> | `404`         | `application/json`                | Company does not exist                    |

##### Example cURL

> ```bash
> curl -X POST "http://localhost:8889/exampleCompany/latest/uint128" -H "Authorization: Bearer <your_jwt_token>" -H "Content-Type: application/json" -d '{"seed": "abcdef1234567890"}'
> ```

##### Sample Output
```json
{
  "round": 12345,
  "randomness": "3c4d5e6f78901234"
}
```

</details>

<details>
 <summary><code>POST</code> <code><b>/{company}/latest/uint256</b></code> <code>(Returns a uint256 derived from the latest randomness beacon)</code></summary>

##### Parameters

- `company` (path parameter, required): Name of the company.

##### Request Body

> | content-type     | schema                            |
> |------------------|-----------------------------------|
> | `application/json`| RandomnessRequest                |

##### Responses

> | http code     | content-type                      | response                                  |
> |---------------|-----------------------------------|-------------------------------------------|
> | `200`         | `application/json`                | RandomnessResponse                        |
> | `401`         | `application/json`                | Unauthorized                              |
> | `404`         | `application/json`                | Company does not exist                    |

##### Example cURL

> ```bash
> curl -X POST "http://localhost:8889/exampleCompany/latest/uint256" -H "Authorization: Bearer <your_jwt_token>" -H "Content-Type: application/json" -d '{"seed": "abcdef1234567890"}'
> ```

##### Sample Output
```json
{
  "round": 12345,
  "randomness": "4d5e6f7890123456"
}
```

</details>

<details>
 <summary><code>POST</code> <code><b>/{company}/latest/in_range</b></code> <code>(Returns a uint256 within the specified [min, max) range derived from the latest randomness beacon)</code></summary>

##### Parameters

- `company` (path parameter, required): Name of the company.

##### Request Body

> | content-type     | schema                            |
> |------------------|-----------------------------------|
> | `application/json`| RandomnessInRangeRequest         |

##### Responses

> | http code     | content-type                      | response                                  |
> |---------------|-----------------------------------|-------------------------------------------|
> | `200`         | `application/json`                | RandomnessResponse                        |
> | `401`         | `application/json`                | Unauthorized                              |
> | `404`         | `application/json`                | Company does not exist                    |

##### Example cURL

> ```bash
> curl -X POST "http://localhost:8889/exampleCompany/latest/in_range" -H "Authorization: Bearer <your_jwt_token>" -H "Content-Type: application/json" -d '{"seed": "abcdef1234567890", "min": "10", "max": "100"}'
> ```

##### Sample Output
```json
{
  "round": 12345,
  "randomness": "5e6f789012345678"
}
```

</details>
