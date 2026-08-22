# Phase 1.1 migration disclosures

This file records required reader-facing explanations for the Phase 1.1 release notes. It is
not evidence that the release has shipped.

## Government-debt definition and source

Required release-note language:

> Debt is now measured on a general-government basis from IMF World Economic Outlook
> `GGXWDG_NGDP`. The previous central-government series covered 15 of the 50 economies at
> the comparison year. The move to 50-of-50 coverage reflects a source and institutional-scope
> change; it does not mean 35 economies began reporting debt.

Classify this under both **Metric definition change** and **Source change**, not as an
ordinary data refresh. General government consolidates central, state or local, and
social-security entities, so values are not continuous with the retired
`central_government_debt_pct_gdp` history.

The release diff must show:

- `central_government_debt_pct_gdp` removed;
- `general_government_gross_debt_pct_gdp` added;
- no observation revisions linking the two identities.

Do not describe the coverage increase as new reporting, improved reporting participation, or
the filling of missing values.
