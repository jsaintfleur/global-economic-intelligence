# Current Government Debt Implementation

Technical summary: this report reproduces current registry, payload, source, and transformation evidence without making a methodological recommendation.

The available metadata identifies **central-government debt**. It does not declare general-government scope or a gross/net basis, so those properties are not inferred. Current methodology text: “Debt is central-government debt, not general-government debt.”

## Central government debt (`central_government_debt_pct_gdp`)

- Indicator: `GC.DOD.TOTL.GD.ZS`; source: World Bank — World Development Indicators.
- Registry definition: Central-government debt as a share of GDP.
- Unit: `% of GDP`. Transformation: `identity` — Preserve the normalized source value.
- Coverage: 35 of 50 countries, 608 observations, 1990-2024. Missing countries: CHN, JPN, FRA, SAU, BEL, IRL, ARG, SWE, AUT, VNM, ROU, HKG, IRN, NGA, DZA.
- Current UI wording: `Central government debt` (short label `Central gov. debt`). Caveat: Central—not general—government debt; coverage is sparse and institutional scope differs.

| Country | ISO3 | Latest year | Latest value |
| --- | --- | --- | --- |
| United States | USA | 2024 | 115.768352618316 |
| China | CHN |  |  |
| Germany | DEU | 1990 | 20.8541847518408 |
| Japan | JPN |  |  |
| United Kingdom | GBR | 2024 | 130.735888365813 |
| India | IND | 2018 | 46.5224986659322 |
| France | FRA |  |  |
| Russian Federation | RUS | 2024 | 17.8500676833114 |
| Italy | ITA | 1992 | 77.2855315218802 |
| Canada | CAN | 2024 | 64.1314232901439 |
| Brazil | BRA | 2024 | 81.8554431191023 |
| Spain | ESP | 2024 | 105.639074777338 |
| Korea, Rep. | KOR | 2024 | 47.8141426119509 |
| Mexico | MEX | 2024 | 50.270950655733 |
| Australia | AUS | 2022 | 57.8834285733848 |
| Turkiye | TUR | 2024 | 26.6192344930079 |
| Indonesia | IDN | 2009 | 29.997306381567 |
| Netherlands | NLD | 1994 | 54.214654102661 |
| Saudi Arabia | SAU |  |  |
| Switzerland | CHE | 2024 | 22.2786942016816 |
| Poland | POL | 1994 | 60.4543984704576 |
| Belgium | BEL |  |  |
| Ireland | IRL |  |  |
| Argentina | ARG |  |  |
| Sweden | SWE |  |  |
| Israel | ISR | 1999 | 88.3064793540794 |
| Singapore | SGP | 2024 | 167.799832036767 |
| Austria | AUT |  |  |
| Thailand | THA | 2024 | 61.861415782411 |
| Norway | NOR | 1994 | 30.9484525212916 |
| Viet Nam | VNM |  |  |
| Philippines | PHL | 2014 | 43.426338941462 |
| Malaysia | MYS | 2024 | 64.566529006102 |
| Denmark | DNK | 1994 | 75.3312600417617 |
| Colombia | COL | 2024 | 71.1965371181288 |
| Bangladesh | BGD | 2003 | 31.2044521104432 |
| Romania | ROU |  |  |
| Hong Kong SAR, China | HKG |  |  |
| South Africa | ZAF | 2024 | 82.7627080034486 |
| Pakistan | PAK | 2000 | 55.0324216144747 |
| Czechia | CZE | 1994 | 13.9974227725367 |
| Egypt, Arab Rep. | EGY | 2007 | 85.7885338345865 |
| Iran, Islamic Rep. | IRN |  |  |
| Chile | CHL | 2000 | 13.1456400046218 |
| Portugal | PRT | 1994 | 5.6574045702943 |
| Peru | PER | 2021 | 35.237190374692 |
| Finland | FIN | 1994 | 58.3135962623348 |
| Kazakhstan | KAZ | 2023 | 20.8858497183933 |
| Nigeria | NGA |  |  |
| Algeria | DZA |  |  |
