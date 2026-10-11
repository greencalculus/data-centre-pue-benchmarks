#!/usr/bin/env python3
"""Build pue-benchmarks.csv from the source snapshot and the hand-checked rows below.

Every row carries the publisher's own figure, the page or document it came from,
and the date we read it. Nothing is estimated, rounded or converted: a value is
written exactly as the publisher printed it (Google "1.1" stays 1.10 only where
Google printed 1.10).

    python3 build.py            # writes pue-benchmarks.csv + pue-benchmarks.json
"""
import csv
import json
import pathlib

HERE = pathlib.Path(__file__).parent
RETRIEVED = "2026-10-11"

FIELDS = [
    "id", "publisher", "scope", "facility_or_region", "country", "period", "period_type",
    "pue", "metric", "boundary_note", "source_title", "source_url", "source_date", "retrieved", "notes",
]

GOOGLE_URL = "https://datacenters.google/efficiency/"
GOOGLE_TITLE = "Google Data Centers: Efficiency (fleet and campus PUE tables)"
GOOGLE_BOUNDARY = "Google: whole large-scale fleet (5 MW reporting threshold), all seasons, all sources of overhead"
AWS_URL = "https://sustainability.aboutamazon.com/products-services/aws-cloud"
AWS_TITLE = "Amazon Sustainability: AWS Cloud (AWS Region PUE and WUE table)"
AWS_BOUNDARY = "AWS: regions with 12+ months of data centre operation; AWS PUE methodology"

# Google campus → ISO 3166-1 alpha-2.
GOOGLE_COUNTRY = {
    "Taiwan": "TW", "Japan": "JP", "Ireland": "IE", "Netherlands": "NL", "Denmark": "DK",
    "Finland": "FI", "Chile": "CL", "Singapore": "SG", "Belgium": "BE",
}
AWS_COUNTRY = {
    "Frankfurt": "DE", "Ireland": "IE", "London": "GB", "Paris": "FR", "Spain": "ES", "Stockholm": "SE",
    "Bahrain": "BH", "Tel Aviv": "IL", "UAE": "AE", "Cape Town": "ZA", "Bangkok": "TH", "Hyderabad": "IN",
    "Jakarta": "ID", "Melbourne": "AU", "Mumbai": "IN", "Osaka": "JP", "Singapore": "SG", "Sydney": "AU",
    "Tokyo": "JP", "Ningxia": "CN", "Sao Paulo": "BR", "Northern Virginia": "US", "Ohio": "US",
    "Northern California": "US", "Oregon": "US", "Central": "CA", "West": "CA",
}


def google_country(name):
    for k, v in GOOGLE_COUNTRY.items():
        if k in name:
            return v
    return "US"


def aws_country(region):
    inner = region[region.find("(") + 1:region.rfind(")")]
    return AWS_COUNTRY.get(inner, "")


def rows():
    snap = json.loads((HERE / "sources_snapshot.json").read_text())
    out = []

    # ── Google: fleet + campuses, Q2 2026 table ───────────────────────────
    for name, q, ttm in snap["google_q2_2026"]:
        is_fleet = name == "Fleet"
        if ttm and ttm not in ("", "-", "--"):
            out.append({
                "publisher": "Google", "scope": "fleet" if is_fleet else "campus",
                "facility_or_region": "Global fleet" if is_fleet else name,
                "country": "" if is_fleet else google_country(name),
                "period": "TTM to Q2 2026", "period_type": "trailing_12_months", "pue": ttm,
                "metric": "operational", "boundary_note": GOOGLE_BOUNDARY,
                "source_title": GOOGLE_TITLE, "source_url": GOOGLE_URL, "source_date": "2026 Q2 table",
                "notes": "" if is_fleet else f"Quarterly PUE Q2 2026: {q}",
            })
        elif q:
            out.append({
                "publisher": "Google", "scope": "campus", "facility_or_region": name, "country": google_country(name),
                "period": "Q2 2026", "period_type": "quarter", "pue": q, "metric": "operational",
                "boundary_note": GOOGLE_BOUNDARY, "source_title": GOOGLE_TITLE, "source_url": GOOGLE_URL,
                "source_date": "2026 Q2 table", "notes": "Less than 12 months of data, so Google shows no TTM value",
            })
    # Google year-end fleet TTM history (Q4 tables).
    for year, fleet in snap["google_q4"]:
        out.append({
            "publisher": "Google", "scope": "fleet", "facility_or_region": "Global fleet", "country": "",
            "period": f"TTM to Q4 {year}", "period_type": "trailing_12_months", "pue": fleet[2],
            "metric": "operational", "boundary_note": GOOGLE_BOUNDARY, "source_title": GOOGLE_TITLE,
            "source_url": GOOGLE_URL, "source_date": f"{year} Q4 table", "notes": f"Quarterly PUE Q4 {year}: {fleet[1]}",
        })

    # ── AWS: region table (2025 column) ───────────────────────────────────
    head = snap["aws_regions"][0]
    i25 = head.index("PUE 2025")
    for r in snap["aws_regions"][1:]:
        v = r[i25]
        if v in ("--", "---", ""):
            continue
        out.append({
            "publisher": "Amazon Web Services", "scope": "cloud_region", "facility_or_region": r[0],
            "country": aws_country(r[0]), "period": "2025", "period_type": "calendar_year", "pue": v,
            "metric": "operational", "boundary_note": AWS_BOUNDARY, "source_title": AWS_TITLE,
            "source_url": AWS_URL, "source_date": "2025 column", "notes": "",
        })

    # ── Hand-checked rows (each read on the source on 2026-10-10) ──────────
    def add(**kw):
        kw.setdefault("notes", "")
        kw.setdefault("boundary_note", "")
        out.append(kw)

    add(publisher="Amazon Web Services", scope="fleet", facility_or_region="Global fleet", country="",
        period="2025", period_type="calendar_year", pue="1.14", metric="operational",
        source_title="AWS Sustainability", source_url="https://aws.amazon.com/sustainability/", source_date="2026",
        notes="'In 2025, our data centers reported an average global PUE of 1.14'")
    add(publisher="Amazon Web Services", scope="fleet", facility_or_region="Global fleet", country="",
        period="2024", period_type="calendar_year", pue="1.15", metric="operational",
        source_title="2024 Amazon Sustainability Report: AWS Summary",
        source_url="https://sustainability.aboutamazon.com/2024-amazon-sustainability-report-aws-summary.pdf",
        source_date="2025", notes="Same document cites IDC estimates of 1.25 (public cloud) and 1.63 (on-premises enterprise)")
    add(publisher="IDC (cited by AWS)", scope="industry_estimate", facility_or_region="Public cloud industry average", country="",
        period="2H 2024", period_type="estimate", pue="1.25", metric="estimate",
        source_title="2024 Amazon Sustainability Report: AWS Summary (citing IDC, 2H24 Datacenter Trends, Doc #US51911924, Jan 2025)",
        source_url="https://sustainability.aboutamazon.com/2024-amazon-sustainability-report-aws-summary.pdf", source_date="2025",
        notes="Secondary: IDC figure as quoted by AWS; the IDC document itself is paywalled")
    add(publisher="IDC (cited by AWS)", scope="industry_estimate", facility_or_region="On-premises enterprise data centres", country="",
        period="2H 2024", period_type="estimate", pue="1.63", metric="estimate",
        source_title="2024 Amazon Sustainability Report: AWS Summary (citing IDC, 2H24 Datacenter Trends, Doc #US51911924, Jan 2025)",
        source_url="https://sustainability.aboutamazon.com/2024-amazon-sustainability-report-aws-summary.pdf", source_date="2025",
        notes="Secondary: IDC figure as quoted by AWS; the IDC document itself is paywalled")

    ms = "https://datacenters.microsoft.com/sustainability/efficiency/"
    mst = "Microsoft Datacenters: Efficiency (PUE and WUE by region)"
    msb = "Microsoft: datacentres Microsoft fully owns and controls, operational for 12 months"
    for region, fy24, fy25 in [("Global", "1.16", "1.17"), ("Americas", "1.16", "1.16"),
                               ("Asia Pacific", "1.25", "1.28"), ("Europe, Middle East & Africa", "1.16", "1.16")]:
        for fy, v, per in [("FY25", fy25, "Jul 2024 to Jun 2025"), ("FY24", fy24, "Jul 2023 to Jun 2024")]:
            add(publisher="Microsoft", scope="fleet" if region == "Global" else "geographic_region",
                facility_or_region=region if region != "Global" else "Global fleet", country="",
                period=f"{fy} ({per})", period_type="fiscal_year", pue=v, metric="operational",
                boundary_note=msb, source_title=mst, source_url=ms, source_date=fy)

    add(publisher="Equinix", scope="fleet", facility_or_region="Global portfolio", country="",
        period="2025", period_type="calendar_year", pue="1.37", metric="operational",
        source_title="Equinix FY2025 Annual Report (SEC Form ARS), chart 'Annualized global average PUE'",
        source_url="https://www.sec.gov/Archives/edgar/data/1101239/000110123926000075/EQIXAnnualRpt2025PRINT.pdf",
        source_date="2026", notes="Chart labels: 2019 baseline 1.54, 2023 1.42, 2024 1.39, 2025 1.37, 2030 target 1.33. The same report cites a 5.3% year-over-year PUE improvement, which the 1.39 to 1.37 change does not match; the published 1.37 is reported here.")
    add(publisher="Equinix", scope="fleet", facility_or_region="Global portfolio", country="",
        period="2024", period_type="calendar_year", pue="1.39", metric="operational",
        source_title="Equinix Inc. Form 10-K for fiscal year 2025 (SEC filing)",
        source_url="https://www.sec.gov/Archives/edgar/data/1101239/000110123926000032/eqix-20251231.htm",
        source_date="2026", notes="'In 2024, we achieved an annual average operational PUE of 1.39, a 6% improvement from 2023'")
    dlr = "https://mfn.se/all/a/digital-realty/digital-realty-publishes-2025-impact-report-highlighting-sustainability-progress-f0a795c9"
    dlrt = "Digital Realty press release: 2025 Impact Report (27 May 2026)"
    add(publisher="Digital Realty", scope="fleet", facility_or_region="Global portfolio", country="", period="2025",
        period_type="calendar_year", pue="1.38", metric="operational", source_title=dlrt, source_url=dlr, source_date="2026-05-27")
    add(publisher="Digital Realty", scope="geographic_region", facility_or_region="EMEA portfolio", country="", period="2025",
        period_type="calendar_year", pue="1.31", metric="operational", source_title=dlrt, source_url=dlr, source_date="2026-05-27")
    add(publisher="Digital Realty", scope="new_builds", facility_or_region="Data centres delivered in 2025 (average)", country="",
        period="2025", period_type="design", pue="1.20", metric="design", source_title=dlrt, source_url=dlr,
        source_date="2026-05-27", notes="Design PUE, not measured operation")

    up = "https://datacenter.uptimeinstitute.com/rs/711-RIA-145/images/2025.Annual.Survey.Report.pdf?version=0"
    upt = "Uptime Institute Global Data Center Survey 2025 (Figure 2)"
    upb = "Survey: respondents' average annual PUE for their data centre (2025: n=681, weighted average)"
    for year, v in [("2007", "2.50"), ("2011", "1.98"), ("2014", "1.65"), ("2018", "1.58"), ("2019", "1.67"),
                    ("2020", "1.59"), ("2021", "1.57"), ("2022", "1.55"), ("2023", "1.58"), ("2024", "1.56"), ("2025", "1.54")]:
        add(publisher="Uptime Institute", scope="industry_survey", facility_or_region="Global survey average", country="",
            period=year, period_type="survey_year", pue=v, metric="survey_average", boundary_note=upb,
            source_title=upt, source_url=up, source_date="2025-07")
    add(publisher="Uptime Institute", scope="industry_survey", facility_or_region="Facilities commissioned from about early 2020",
        country="", period="2025", period_type="survey_year", pue="1.48", metric="survey_average", boundary_note=upb,
        source_title=upt, source_url=up, source_date="2025-07")
    add(publisher="Uptime Institute", scope="industry_survey", facility_or_region="Data centres of 20 MW and above",
        country="", period="2025", period_type="survey_year", pue="1.44", metric="survey_average", boundary_note=upb,
        source_title=upt, source_url=up, source_date="2025-07")

    ec = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:52026DC0500"
    ect = "European Commission, COM(2026) 500 final: Report on the energy efficiency of data centres in the EU (21 Sep 2026)"
    ecb = "EU: data centres of 500 kW+ installed IT power reporting under Delegated Regulation (EU) 2024/1364"
    add(publisher="European Commission", scope="regulatory_average", facility_or_region="EU reporting data centres (average)",
        country="", period="2024", period_type="calendar_year", pue="1.36", metric="regulatory_average", boundary_note=ecb,
        source_title=ect, source_url=ec, source_date="2026-09-21", notes="National averages range from 1.15 to 1.66")
    add(publisher="European Commission", scope="regulatory_average", facility_or_region="EU data centres of 500 to 1,000 kW (average)",
        country="", period="2024", period_type="calendar_year", pue="1.64", metric="regulatory_average", boundary_note=ecb,
        source_title=ect, source_url=ec, source_date="2026-09-21")

    add(publisher="National Laboratory of the Rockies (formerly NREL)", scope="facility",
        facility_or_region="Energy Systems Integration Facility (ESIF) data centre, Golden, Colorado", country="US",
        period="annualised", period_type="annualised", pue="1.036", metric="operational",
        source_title="Measuring Efficiency: PUE (ESIF data centre)",
        source_url="https://www.nlr.gov/computational-science/measuring-efficiency-pue", source_date="page read 2026-10-10",
        notes="Design requirement: annualised PUE of 1.06 or better")

    for n, r in enumerate(out, 1):
        r["id"] = f"pue-{n:04d}"
        r["retrieved"] = RETRIEVED
    return out


def main():
    data = rows()
    with open(HERE / "pue-benchmarks.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in data:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    (HERE / "pue-benchmarks.json").write_text(json.dumps({"retrieved": RETRIEVED, "rows": data}, indent=1, ensure_ascii=False))
    print(f"{len(data)} rows")


if __name__ == "__main__":
    main()
