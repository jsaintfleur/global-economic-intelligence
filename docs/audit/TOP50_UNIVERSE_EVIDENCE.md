# Top-50 Universe Evidence

Technical summary: release `release_c95979a1f2a0d628fbf3` uses one common GDP observation year, `2025`, for every selected World Bank-covered economy in the approved cohort. This does not establish candidate-universe completeness.

## Implemented selection rule

- Indicator: World Bank WDI `NY.GDP.MKTP.CD` (nominal GDP, current US$).
- Eligibility policy: explicit `phase_1_1_v1` registry records.
- Provider: normalized World Bank GDP observations; `gei.universe.select_universe` is source-neutral.
- Reference year: latest year containing all 50 approved entities; current result `2025`.
- Ranking: GDP descending, then ISO3 ascending; exactly 50 eligible entities selected.
- Candidate-universe completeness: false; the current provider omits analytical candidates including Taiwan.

## Selected economies

| Rank | Economy | ISO3 | GDP value | Year |
| --- | --- | --- | --- | --- |
| 1 | United States | USA | 30769700000000 | 2025 |
| 2 | China | CHN | 19498039388042.6 | 2025 |
| 3 | Germany | DEU | 5050922925047.05 | 2025 |
| 4 | Japan | JPN | 4435162999976.94 | 2025 |
| 5 | United Kingdom | GBR | 4002587541846.01 | 2025 |
| 6 | India | IND | 3956067115771.63 | 2025 |
| 7 | France | FRA | 3366315927447.33 | 2025 |
| 8 | Russian Federation | RUS | 2561310169358.74 | 2025 |
| 9 | Italy | ITA | 2551556954100.35 | 2025 |
| 10 | Canada | CAN | 2319899772425.92 | 2025 |
| 11 | Brazil | BRA | 2279920092492.13 | 2025 |
| 12 | Spain | ESP | 1906453309985.88 | 2025 |
| 13 | Korea, Rep. | KOR | 1872374961553.15 | 2025 |
| 14 | Mexico | MEX | 1832641364775.52 | 2025 |
| 15 | Australia | AUS | 1798518933689.21 | 2025 |
| 16 | Turkiye | TUR | 1597293229287 | 2025 |
| 17 | Indonesia | IDN | 1445642584163.81 | 2025 |
| 18 | Netherlands | NLD | 1332767651100.39 | 2025 |
| 19 | Saudi Arabia | SAU | 1276942933333.33 | 2025 |
| 20 | Switzerland | CHE | 1043529899250.92 | 2025 |
| 21 | Poland | POL | 1035491784197.44 | 2025 |
| 22 | Belgium | BEL | 725466462859.646 | 2025 |
| 23 | Ireland | IRL | 721701359046.313 | 2025 |
| 24 | Argentina | ARG | 683097891618.597 | 2025 |
| 25 | Sweden | SWE | 668998664082.081 | 2025 |
| 26 | Israel | ISR | 610777842873.595 | 2025 |
| 27 | Singapore | SGP | 603869516998.738 | 2025 |
| 28 | Austria | AUT | 579470021095.418 | 2025 |
| 29 | Thailand | THA | 577009981112.015 | 2025 |
| 30 | Norway | NOR | 530755719438.879 | 2025 |
| 31 | Viet Nam | VNM | 514697215165.065 | 2025 |
| 32 | Philippines | PHL | 487086123720.417 | 2025 |
| 33 | Malaysia | MYS | 472193128644.597 | 2025 |
| 34 | Denmark | DNK | 462526660468.393 | 2025 |
| 35 | Colombia | COL | 457410034202.523 | 2025 |
| 36 | Bangladesh | BGD | 456319229255.578 | 2025 |
| 37 | Romania | ROU | 428677977854.826 | 2025 |
| 38 | Hong Kong SAR, China | HKG | 427310315921.993 | 2025 |
| 39 | South Africa | ZAF | 427184325997.307 | 2025 |
| 40 | Pakistan | PAK | 407307214476.222 | 2025 |
| 41 | Czechia | CZE | 391026962800.475 | 2025 |
| 42 | Egypt, Arab Rep. | EGY | 365254630179.737 | 2025 |
| 43 | Iran, Islamic Rep. | IRN | 362682115433.364 | 2025 |
| 44 | Chile | CHL | 357371159574.862 | 2025 |
| 45 | Portugal | PRT | 346639825141.821 | 2025 |
| 46 | Peru | PER | 334854659181.893 | 2025 |
| 47 | Finland | FIN | 317039368819.607 | 2025 |
| 48 | Kazakhstan | KAZ | 306239209650.024 | 2025 |
| 49 | Nigeria | NGA | 290794361542.112 | 2025 |
| 50 | Algeria | DZA | 287031225987.736 | 2025 |

## Cutoff neighborhood (ranks 45-55)

| Rank | Economy | ISO3 | GDP value | Selected |
| --- | --- | --- | --- | --- |
| 45 | Portugal | PRT | 346639825141.821 | True |
| 46 | Peru | PER | 334854659181.893 | True |
| 47 | Finland | FIN | 317039368819.607 | True |
| 48 | Kazakhstan | KAZ | 306239209650.024 | True |
| 49 | Nigeria | NGA | 290794361542.112 | True |
| 50 | Algeria | DZA | 287031225987.736 | True |
| 51 | Greece | GRC | 280635521324.441 | False |
| 52 | New Zealand | NZL | 264057413739.965 | False |
| 53 | Iraq | IRQ | 254367293538.462 | False |
| 54 | Hungary | HUN | 246490213513.054 | False |
| 55 | Qatar | QAT | 215559615384.615 | False |

## Missing reference-year candidates

31 canonical non-aggregate country-dimension entries have no usable GDP value in `2025`. See the machine-readable exclusion file for the exact list.

## Analytical-entity evidence boundary

Atlas does not infer sovereignty. The explicit eligibility registry records Taiwan as `pending_review`, identifies it with IMF WEO code `TWN`, and leaves its World Bank code null. Common-year consistency among World Bank-covered entities does not resolve this source-universe omission.

Files: [`top50_universe_candidates.csv`](../../data/audit/release_c95979a1f2a0d628fbf3/top50_universe_candidates.csv), [`top50_universe_missing_reference_year.csv`](../../data/audit/release_c95979a1f2a0d628fbf3/top50_universe_missing_reference_year.csv), and adjacent JSON.
