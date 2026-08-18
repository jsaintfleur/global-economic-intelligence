# Current GDP, GDP Per Capita, and Growth Implementation

Technical summary: this report reproduces current registry, payload, source, and transformation evidence without making a methodological recommendation.

Current methodology text: “Nominal GDP and GDP per capita use current US dollars. GDP growth is the World Bank constant-local-currency annual growth series. CPI inflation is annual percent change. Unemployment is the modeled ILO estimate. Debt is central-government debt, not general-government debt.” Structural bases are exactly those stated in each registry definition and unit below.

## Nominal GDP (`gdp_current_usd`)

- Indicator: `NY.GDP.MKTP.CD`; source: World Bank — World Development Indicators.
- Registry definition: Gross domestic product at current market prices converted to current US dollars.
- Unit: `current US$`. Transformation: `identity` — Preserve the normalized source value.
- Coverage: 50 of 50 countries, 1800 observations, 1990-2025. Missing countries: none.
- Current UI wording: `Nominal GDP` (short label `GDP`). Caveat: Exchange-rate movements affect cross-country levels and ranks.

| Country | ISO3 | Latest year | Latest value |
| --- | --- | --- | --- |
| United States | USA | 2025 | 30769700000000.0 |
| China | CHN | 2025 | 19498039388042.6 |
| Germany | DEU | 2025 | 5050922925047.05 |
| Japan | JPN | 2025 | 4435162999976.94 |
| United Kingdom | GBR | 2025 | 4002587541846.01 |
| India | IND | 2025 | 3956067115771.63 |
| France | FRA | 2025 | 3366315927447.33 |
| Russian Federation | RUS | 2025 | 2561310169358.74 |
| Italy | ITA | 2025 | 2551556954100.35 |
| Canada | CAN | 2025 | 2319899772425.92 |
| Brazil | BRA | 2025 | 2279920092492.13 |
| Spain | ESP | 2025 | 1906453309985.88 |
| Korea, Rep. | KOR | 2025 | 1872374961553.15 |
| Mexico | MEX | 2025 | 1832641364775.52 |
| Australia | AUS | 2025 | 1798518933689.21 |
| Turkiye | TUR | 2025 | 1597293229287.0 |
| Indonesia | IDN | 2025 | 1445642584163.81 |
| Netherlands | NLD | 2025 | 1332767651100.39 |
| Saudi Arabia | SAU | 2025 | 1276942933333.33 |
| Switzerland | CHE | 2025 | 1043529899250.92 |
| Poland | POL | 2025 | 1035491784197.44 |
| Belgium | BEL | 2025 | 725466462859.646 |
| Ireland | IRL | 2025 | 721701359046.313 |
| Argentina | ARG | 2025 | 683097891618.597 |
| Sweden | SWE | 2025 | 668998664082.081 |
| Israel | ISR | 2025 | 610777842873.595 |
| Singapore | SGP | 2025 | 603869516998.738 |
| Austria | AUT | 2025 | 579470021095.418 |
| Thailand | THA | 2025 | 577009981112.015 |
| Norway | NOR | 2025 | 530755719438.879 |
| Viet Nam | VNM | 2025 | 514697215165.065 |
| Philippines | PHL | 2025 | 487086123720.417 |
| Malaysia | MYS | 2025 | 472193128644.597 |
| Denmark | DNK | 2025 | 462526660468.393 |
| Colombia | COL | 2025 | 457410034202.523 |
| Bangladesh | BGD | 2025 | 456319229255.578 |
| Romania | ROU | 2025 | 428677977854.826 |
| Hong Kong SAR, China | HKG | 2025 | 427310315921.993 |
| South Africa | ZAF | 2025 | 427184325997.307 |
| Pakistan | PAK | 2025 | 407307214476.222 |
| Czechia | CZE | 2025 | 391026962800.475 |
| Egypt, Arab Rep. | EGY | 2025 | 365254630179.737 |
| Iran, Islamic Rep. | IRN | 2025 | 362682115433.364 |
| Chile | CHL | 2025 | 357371159574.862 |
| Portugal | PRT | 2025 | 346639825141.821 |
| Peru | PER | 2025 | 334854659181.893 |
| Finland | FIN | 2025 | 317039368819.607 |
| Kazakhstan | KAZ | 2025 | 306239209650.024 |
| Nigeria | NGA | 2025 | 290794361542.112 |
| Algeria | DZA | 2025 | 287031225987.736 |

## GDP per capita (`gdp_per_capita_current_usd`)

- Indicator: `NY.GDP.PCAP.CD`; source: World Bank — World Development Indicators.
- Registry definition: Nominal GDP per person in current US dollars.
- Unit: `current US$ per person`. Transformation: `identity` — Preserve the normalized source value.
- Coverage: 50 of 50 countries, 1800 observations, 1990-2025. Missing countries: none.
- Current UI wording: `GDP per capita` (short label `GDP/person`). Caveat: Current-dollar levels are not purchasing-power adjusted.

| Country | ISO3 | Latest year | Latest value |
| --- | --- | --- | --- |
| United States | USA | 2025 | 90026.5163005744 |
| China | CHN | 2025 | 13861.970224368 |
| Germany | DEU | 2025 | 60496.4350820414 |
| Japan | JPN | 2025 | 35951.0449549304 |
| United Kingdom | GBR | 2025 | 57601.9621201954 |
| India | IND | 2025 | 2702.47987141553 |
| France | FRA | 2025 | 48985.7307807924 |
| Russian Federation | RUS | 2025 | 17546.609375 |
| Italy | ITA | 2025 | 43308.6403060733 |
| Canada | CAN | 2025 | 55697.6639660837 |
| Brazil | BRA | 2025 | 10713.2856869511 |
| Spain | ESP | 2025 | 38627.2472148623 |
| Korea, Rep. | KOR | 2025 | 36226.9663637512 |
| Mexico | MEX | 2025 | 13889.2339628708 |
| Australia | AUS | 2025 | 65129.7227990563 |
| Turkiye | TUR | 2025 | 18599.4420922378 |
| Indonesia | IDN | 2025 | 5059.62596411213 |
| Netherlands | NLD | 2025 | 73683.917132794 |
| Saudi Arabia | SAU | 2025 | 34536.6555456551 |
| Switzerland | CHE | 2025 | 114769.012314293 |
| Poland | POL | 2025 | 28419.5777395638 |
| Belgium | BEL | 2025 | 60750.2735864647 |
| Ireland | IRL | 2025 | 131592.462547877 |
| Argentina | ARG | 2025 | 14898.0885943842 |
| Sweden | SWE | 2025 | 63133.2126736715 |
| Israel | ISR | 2025 | 60336.8477964194 |
| Singapore | SGP | 2025 | 98813.9788172877 |
| Austria | AUT | 2025 | 62930.0351324599 |
| Thailand | THA | 2025 | 8056.56359761558 |
| Norway | NOR | 2025 | 94594.1929573987 |
| Viet Nam | VNM | 2025 | 5065.99091899299 |
| Philippines | PHL | 2025 | 4170.72347271451 |
| Malaysia | MYS | 2025 | 13124.5554178269 |
| Denmark | DNK | 2025 | 76970.1535217919 |
| Colombia | COL | 2025 | 8561.62091854449 |
| Bangladesh | BGD | 2025 | 2597.34352335275 |
| Romania | ROU | 2025 | 22537.9532108047 |
| Hong Kong SAR, China | HKG | 2025 | 56983.0663059906 |
| South Africa | ZAF | 2025 | 6597.71450918774 |
| Pakistan | PAK | 2025 | 1595.90912252837 |
| Czechia | CZE | 2025 | 35917.2724081665 |
| Egypt, Arab Rep. | EGY | 2025 | 3085.80712036204 |
| Iran, Islamic Rep. | IRN | 2025 | 3924.38017821898 |
| Chile | CHL | 2025 | 17994.5911957485 |
| Portugal | PRT | 2025 | 32081.8106150292 |
| Peru | PER | 2025 | 9684.41170314988 |
| Finland | FIN | 2025 | 56148.580949046 |
| Kazakhstan | KAZ | 2025 | 14692.1331757237 |
| Nigeria | NGA | 2025 | 1224.25410237743 |
| Algeria | DZA | 2025 | 6051.00322704182 |

## Real GDP growth (`gdp_growth_pct`)

- Indicator: `NY.GDP.MKTP.KD.ZG`; source: World Bank — World Development Indicators.
- Registry definition: Annual growth rate of GDP at market prices based on constant local currency.
- Unit: `% annual change`. Transformation: `identity` — Preserve the normalized source value.
- Coverage: 50 of 50 countries, 1796 observations, 1990-2025. Missing countries: none.
- Current UI wording: `Real GDP growth` (short label `GDP growth`). Caveat: Constant-price growth; revisions are common.

| Country | ISO3 | Latest year | Latest value |
| --- | --- | --- | --- |
| United States | USA | 2025 | 2.16138195623856 |
| China | CHN | 2025 | 4.95994886240992 |
| Germany | DEU | 2025 | 0.239578342117881 |
| Japan | JPN | 2025 | 1.19311288444599 |
| United Kingdom | GBR | 2025 | 1.38844207858726 |
| India | IND | 2025 | 7.56666179284244 |
| France | FRA | 2025 | 0.840949955479587 |
| Russian Federation | RUS | 2025 | 1.00117656925738 |
| Italy | ITA | 2025 | 0.539583636778445 |
| Canada | CAN | 2025 | 1.74268536175708 |
| Brazil | BRA | 2025 | 2.2857464902475 |
| Spain | ESP | 2025 | 2.82495400578509 |
| Korea, Rep. | KOR | 2025 | 1.00701840291242 |
| Mexico | MEX | 2025 | 0.561683456144578 |
| Australia | AUS | 2025 | 1.35039785076631 |
| Turkiye | TUR | 2025 | 3.60462514082589 |
| Indonesia | IDN | 2025 | 5.10808904438025 |
| Netherlands | NLD | 2025 | 1.78463214703797 |
| Saudi Arabia | SAU | 2025 | 4.50246560191663 |
| Switzerland | CHE | 2025 | 1.30007790958307 |
| Poland | POL | 2025 | 3.5727250346774 |
| Belgium | BEL | 2025 | 0.983117967125935 |
| Ireland | IRL | 2025 | 12.3375990291434 |
| Argentina | ARG | 2025 | 4.36733330217022 |
| Sweden | SWE | 2025 | 1.54316373266217 |
| Israel | ISR | 2025 | 2.93114966387968 |
| Singapore | SGP | 2025 | 5.02588199508003 |
| Austria | AUT | 2025 | 0.615747280959056 |
| Thailand | THA | 2025 | 2.44247444990198 |
| Norway | NOR | 2025 | 1.08528185031417 |
| Viet Nam | VNM | 2025 | 8.01882998978245 |
| Philippines | PHL | 2025 | 4.40240158710621 |
| Malaysia | MYS | 2025 | 5.17127082911057 |
| Denmark | DNK | 2025 | 2.92843280014236 |
| Colombia | COL | 2025 | 2.64201548985928 |
| Bangladesh | BGD | 2025 | 3.48990671836833 |
| Romania | ROU | 2025 | 0.677829835052762 |
| Hong Kong SAR, China | HKG | 2025 | 3.48764886355949 |
| South Africa | ZAF | 2025 | 1.11462608103956 |
| Pakistan | PAK | 2025 | 3.69842668749033 |
| Czechia | CZE | 2025 | 2.58046673293437 |
| Egypt, Arab Rep. | EGY | 2025 | 4.39201068570188 |
| Iran, Islamic Rep. | IRN | 2025 | -2.82597163290347 |
| Chile | CHL | 2025 | 2.45925474781374 |
| Portugal | PRT | 2025 | 1.86448007464475 |
| Peru | PER | 2025 | 3.43056395124466 |
| Finland | FIN | 2025 | 0.173444509584499 |
| Kazakhstan | KAZ | 2025 | 6.5 |
| Nigeria | NGA | 2025 | 4.01336180700973 |
| Algeria | DZA | 2025 | 3.815543719231 |
