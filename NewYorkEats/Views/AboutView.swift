import SwiftUI

struct AboutView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Text("NEW YORK EATS").displayFont(30).foregroundStyle(Theme.navy)
                    Text("A free guide to \(model.restaurantCount.formatted()) restaurants across New York State, with hand-checked lists of slice shops, bagels and delis, Buffalo wings and beef on weck, upstate hots, Utica and Binghamton classics and dim sum, and New York City's official letter grades. No account, no ads, no tracking.")
                        .font(.subheadline).foregroundStyle(Theme.ink2)
                    Text("\(Links.appName) (\u{201C}NY Eats\u{201D}) is an independent app by Nicholas Soderstrom. It is not affiliated with, endorsed by or operated by the State of New York, its Department of Health, State Liquor Authority or Empire State Development, the City of New York or its Department of Health and Mental Hygiene, Suffolk County, Erie County, the City of Buffalo, Michelin, the James Beard Foundation, Apple, or any restaurant, team or chain.")
                        .font(.footnote).foregroundStyle(Theme.muted)
                }
                .padding(.vertical, 4)
            }
            Section("How the lists are built") {
                Text("Slices and pizza styles, bagels, delis and appetizing, wings and beef on weck, hots and plates, Utica and Binghamton classics, dim sum and the oldest places are hand-checked: each was checked in October 2026 against a 2025 or 2026 source (the place's own website or menu, local news, or a tourism listing), with the address checked.")
                Text("The rest come from Overture Maps' open place data and official lists: the NYC Health Department's restaurant permits, the New York State Department of Health's food service permits, Suffolk County's inspections, the City of Buffalo's restaurant licenses and the State Liquor Authority's licenses. Map listings are kept only when they proved reliable: checked against New York City's permits, high-confidence listings matched a permitted food business \(rate("nyc_dohmh", "Meta, confidence 0.95+")) of the time. Website links are checked, and any that no longer belong to the place are left out.")
                Text("Inspection results stay with the agency that published them. In New York City, the letter grade is the Health Department's own, shown with its date. Elsewhere in the state there is no official grade, and this app doesn't make one: it shows the date of the latest state inspection and its counts, or, in Suffolk County, the violations cited in 2025.")
                Text("Ratings, reviews, hours and photos are Apple Maps' own, shown live in Apple's place card. This app doesn't store or rank by them.")
            }
            .font(.subheadline).foregroundStyle(Theme.ink2)
            Section("Sources") {
                source("Overture Maps Foundation", "Restaurant listings and websites come from Overture Maps Foundation places data (overturemaps.org), release 2026-09-23.1, filtered and reformatted for this app.\n• Data from Meta, Microsoft, DAC and BrightQuery. Available under CDLA Permissive 2.0.\n• Data from Foursquare. Copyright 2024 Foursquare Labs, Inc. All rights reserved. Available under Apache 2.0. Foursquare data was transformed to the Overture schema; this app further filtered and reformatted it. See the NOTICE below.\n• Data from AllThePlaces. Available under CC0 1.0.", "https://overturemaps.org")
                source("NYC Department of Health and Mental Hygiene", "New York City Restaurant Inspection Results (NYC Open Data), records through \(model.recordsThrough?.nyc ?? "—"): trade name, address, letter grade and its date, latest inspection, score, critical violations and pests cited. Shown as published; the City makes no warranty as to the data's accuracy, completeness or timeliness and does not endorse this app.", "https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j")
                source("New York State Department of Health", "Food Service Establishment inspections (health.data.ny.gov), records through \(model.recordsThrough?.nysdoh ?? "—"), for every county except New York City, Suffolk and Erie. \u{201C}The inspection data contained in this dataset was not collected in a manner intended for use as a restaurant grading system, and should not be construed or interpreted as such. Any use of this data to develop a restaurant grading system is not supported or endorsed by the New York State Department of Health.\u{201D} Any analyses, interpretations or conclusions in this app are its own, not NYSDOH's.", "https://health.data.ny.gov/Health/Food-Service-Establishment-Last-Inspection/cnih-y5dw")
                source("Suffolk County Department of Health Services", "Restaurant Violations: 2025 (opendata.suffolkcountyny.gov): violations cited in 2025, shown as counts with the latest date.", "https://opendata.suffolkcountyny.gov")
                source("New York State Liquor Authority", "Current Liquor Authority Active Licenses (data.ny.gov): on-premises licenses, used for the trade name, address and license type only. Legal names are never shown.", "https://data.ny.gov/Economic-Development/Current-Liquor-Authority-Active-Licenses/9s3h-dpkz")
                source("City of Buffalo", "Restaurant Licenses (data.buffalony.gov, public domain), used to confirm places at a licensed address. The City makes no warranty and does not endorse this app.", "https://data.buffalony.gov")
                source("Places and outlines", "U.S. Census Bureau cartographic boundary files, 2025 (public domain), for counties, towns and cities; NYC Department of City Planning's 2020 Neighborhood Tabulation Areas (NYC Open Data) for New York City neighborhoods.", nil)
                source("Honors", "The MICHELIN Guide New York 2025 selection (stars and Bib Gourmand) and James Beard Foundation awards, nominees, semifinalists and America's Classics, 2023 to 2026, are reported as facts and checked by hand against public announcements. MICHELIN and the MICHELIN Guide are trademarks of Michelin. James Beard Foundation and James Beard Award are trademarks of the James Beard Foundation. Other names belong to their owners.", nil)
                source("Maps", "Maps, place cards and directions by Apple Maps.", nil)
            }
            Section("Licenses") {
                NavigationLink("Community Data License Agreement – Permissive 2.0") { LicenseText(file: "CDLA-Permissive-2.0", title: "CDLA Permissive 2.0") }
                NavigationLink("Apache License 2.0") { LicenseText(file: "Apache-2.0", title: "Apache License 2.0") }
                NavigationLink("Foursquare OS Places NOTICE") { LicenseText(file: "Foursquare-NOTICE", title: "Foursquare NOTICE") }
            }
            Section("Privacy") {
                Text("The app collects nothing. Your location, if you allow it, only sorts lists by distance and shows where you are on the map, on this device. Saved places stay on this device.")
                    .font(.subheadline).foregroundStyle(Theme.ink2)
                Link("Privacy policy", destination: Links.privacy)
                Link("Terms of use", destination: Links.terms)
            }
            Section("Help") {
                Link("Report a missing or closed place", destination: Links.correctionEmail)
                Link("Email \(Links.supportEmail)", destination: URL(string: "mailto:\(Links.supportEmail)")!)
                Link("Website", destination: Links.site)
                Text("Data as of \(model.generated). Places open and close; check before you go. Version \(Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "1.0")")
                    .font(.footnote).foregroundStyle(Theme.muted)
            }
        }
        .navigationTitle("About")
        .tint(Theme.navy)
    }

    private func rate(_ area: String, _ group: String) -> String {
        guard let g = model.calibration[area]?[group] else { return "most" }
        return "\(Int((g.matched * 100).rounded()))%"
    }

    @ViewBuilder
    private func source(_ name: String, _ detail: String, _ url: String?) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            if let url, let u = URL(string: url) { Link(name, destination: u).font(.subheadline.weight(.semibold)) }
            else { Text(name).font(.subheadline.weight(.semibold)) }
            Text(detail).font(.caption).foregroundStyle(Theme.muted)
        }
    }
}

/// A bundled license text (Resources/Licenses), reflowed rather than shown as raw 80-column lines.
struct LicenseText: View {
    let file: String
    let title: String

    var body: some View {
        ScrollView {
            Text(text).font(.footnote).foregroundStyle(Theme.ink).textSelection(.enabled)
                .frame(maxWidth: .infinity, alignment: .leading).padding()
        }
        .navigationTitle(title)
        .navigationBarTitleDisplayMode(.inline)
    }

    private var text: String {
        guard let url = Bundle.main.url(forResource: file, withExtension: "txt"),
              let raw = try? String(contentsOf: url, encoding: .utf8) else { return "License text missing." }
        // join hard-wrapped lines into paragraphs; keep blank lines and list items as breaks
        var out: [String] = []
        for para in raw.components(separatedBy: "\n\n") {
            let lines = para.components(separatedBy: "\n").map { $0.trimmingCharacters(in: .whitespaces) }
            var joined = ""
            for l in lines where !l.isEmpty {
                let startsItem = l.hasPrefix("–") || l.hasPrefix("-") || l.range(of: #"^\(?[a-z0-9]{1,3}[.)]\s"#, options: .regularExpression) != nil
                joined += joined.isEmpty ? l : (startsItem ? "\n" + l : " " + l)
            }
            if !joined.isEmpty { out.append(joined) }
        }
        return out.joined(separator: "\n\n")
    }
}
