import SwiftUI
import MapKit

struct PlaceDetailView: View {
    @Environment(AppModel.self) private var model
    @Environment(LocationService.self) private var location
    let place: Place

    @Environment(\.dynamicTypeSize) private var typeSize
    @State private var mapItem: MKMapItem?
    @State private var lookingUp = false
    @State private var notOnAppleMaps = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                header
                actions
                if let c = place.coordinate { mapSnippet(c) }
                if place.handChecked { checked }
                if place.jamesBeard != nil || place.michelin != nil { honors }
                if let n = place.nyc { nycInspection(n) }
                if let st = place.stateInspection { stateInspection(st) }
                if let sf = place.suffolk { suffolkViolations(sf) }
                listing
            }
            .padding(16)
        }
        .background(Theme.surface)
        .navigationTitle(place.name)
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItemGroup(placement: .topBarTrailing) {
                Button { model.toggleSaved(place) } label: {
                    Label(model.isSaved(place) ? "Saved" : "Save", systemImage: model.isSaved(place) ? "heart.fill" : "heart")
                }
                ShareLink(item: shareText) { Label("Share", systemImage: "square.and.arrow.up") }
            }
        }
        .mapItemDetailSheet(item: $mapItem)
        .alert("Not on Apple Maps", isPresented: $notOnAppleMaps) {
            Button("Open Apple Maps anyway") { AppleMaps.openInMaps(place) }
            Button("OK", role: .cancel) {}
        } message: {
            Text("Apple Maps doesn't have a listing for \(place.name) at this spot, so there are no ratings or hours to show here.")
        }
    }

    // MARK: sections

    private var header: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text((place.placeName ?? "New York").uppercased())
                .font(.caption.weight(.bold)).tracking(1.2).foregroundStyle(Theme.navy2)
            Text(place.name.uppercased())
                .displayFont(38).foregroundStyle(Theme.navy)
                .fixedSize(horizontal: false, vertical: true)
                .accessibilityAddTraits(.isHeader)
            Text([place.fullAddress, place.cuisine].filter { !$0.isEmpty }.joined(separator: " · "))
                .font(.subheadline).foregroundStyle(Theme.ink2)
                .textSelection(.enabled)
            if let here = model.screenshotLocation ?? location.location, let l = place.location {
                Text("\(here.milesText(to: l)) away").font(.subheadline).foregroundStyle(Theme.muted)
            }
            PlaceChips(place: place)
        }
    }

    private var actions: some View {
        VStack(spacing: 10) {
            Button {
                lookingUp = true
                Task {
                    let item = await AppleMaps.findItem(for: place)
                    lookingUp = false
                    if let item { mapItem = item } else { notOnAppleMaps = true }
                }
            } label: {
                // at the largest text sizes the caption goes under the title, so "Ratings" isn't split across lines
                let layout = typeSize.isAccessibilitySize ? AnyLayout(VStackLayout(alignment: .leading, spacing: 4)) : AnyLayout(HStackLayout())
                layout {
                    HStack {
                        if lookingUp { ProgressView().tint(.white) } else { Image(systemName: "star.bubble") }
                        Text("Ratings, hours & photos").fontWeight(.semibold)
                    }
                    if !typeSize.isAccessibilitySize { Spacer() }
                    Text("Apple Maps").font(.caption)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(14)
                .foregroundStyle(.white)
                .background(RoundedRectangle(cornerRadius: 12).fill(Theme.navy))
            }
            .disabled(place.coordinate == nil || lookingUp)
            .accessibilityHint("Opens the Apple Maps place card with current ratings and hours")

            HStack(spacing: 10) {
                actionButton("Directions", "arrow.triangle.turn.up.right.diamond") { AppleMaps.openInMaps(place, directions: true) }
                if let phone = place.phone, let url = URL(string: "tel:\(phone.filter { $0.isNumber || $0 == "+" })") {
                    actionButton("Call", "phone") { UIApplication.shared.open(url) }
                }
                if let web = place.website {
                    actionButton("Website", "safari") { UIApplication.shared.open(web) }
                }
            }
        }
    }

    private func actionButton(_ title: String, _ icon: String, _ action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: 4) {
                Image(systemName: icon).font(.title3)
                Text(title).font(.caption.weight(.semibold))
            }
            .frame(maxWidth: .infinity, minHeight: 56)
            .foregroundStyle(Theme.navy)
            .background(RoundedRectangle(cornerRadius: 12).strokeBorder(Theme.rule2))
        }
    }

    private func mapSnippet(_ c: CLLocationCoordinate2D) -> some View {
        Map(initialPosition: .region(MKCoordinateRegion(center: c, latitudinalMeters: 900, longitudinalMeters: 900)), interactionModes: []) {
            Marker(place.name, systemImage: MarkerGlyph.symbol(for: place), coordinate: c).tint(place.handChecked ? Theme.markerAccent : Theme.navy)
        }
        .frame(height: 170)
        .clipShape(RoundedRectangle(cornerRadius: 14))
        .onTapGesture { AppleMaps.openInMaps(place) }
        .accessibilityLabel("Map of \(place.name). Opens Apple Maps.")
    }

    private var checked: some View {
        section("Hand-checked", icon: "checkmark.seal.fill", tint: Theme.accentSoft) {
            VStack(alignment: .leading, spacing: 8) {
                if let note = place.note { Text(note).font(.subheadline).foregroundStyle(Theme.ink2) }
                if !place.kinds.names.isEmpty { fact("On our lists", place.kinds.names.joined(separator: ", ")) }
                if let d = place.dishes { fact("Known for", d) }
                if let s = place.season { fact("Season", s) } else if place.isSeasonal { fact("Season", "Seasonal; check before you go.") }
                if let f = place.founded { fact("At this address since", "\(f)") }
                if let b = place.branchOf { fact("A branch of", b) }
                Text("Checked open in October 2026 against a 2025 or 2026 source: the place's own site or menu, local news, or a tourism listing. Hours and menus change, so check before you go.")
                    .font(.caption).foregroundStyle(Theme.ink2)
            }
        }
    }

    private var honors: some View {
        section("Honors", icon: "rosette") {
            VStack(alignment: .leading, spacing: 8) {
                if let m = place.michelin {
                    Label("\(m.label) · MICHELIN Guide New York, 2025 selection", systemImage: "rosette").font(.subheadline).foregroundStyle(Theme.ink)
                }
                ForEach(lines(place.jamesBeard, prefix: "James Beard: "), id: \.self) { l in
                    Label(l, systemImage: "rosette").font(.subheadline).foregroundStyle(Theme.ink)
                }
                if let chef = place.chef { fact("Chef", chef) }
                Text("Honors are facts, not ratings. MICHELIN and the MICHELIN Guide are trademarks of Michelin. James Beard Foundation and James Beard Award are trademarks of the James Beard Foundation.")
                    .font(.caption).foregroundStyle(Theme.muted)
            }
        }
    }

    /// NYC: the letter grade the Health Department posts at the door, with its date. Never computed from the score.
    private func nycInspection(_ n: NYCInspection) -> some View {
        section("Health inspections · NYC Health Department", icon: "checkmark.shield") {
            VStack(alignment: .leading, spacing: 8) {
                if let g = n.g, let meaning = n.gradeMeaning {
                    HStack(spacing: 12) {
                        GradeBadge(grade: g, size: 46)
                        VStack(alignment: .leading, spacing: 2) {
                            Text("\(meaning) · official").font(.headline).foregroundStyle(Theme.ink)
                            if let gd = n.gd { Text("Graded \(Self.date(gd))").font(.subheadline).foregroundStyle(Theme.ink2) }
                        }
                    }
                } else {
                    Text("No letter grade on file yet.").font(.subheadline).foregroundStyle(Theme.ink2)
                }
                if let d = n.d { kv("Latest inspection", Self.date(d)) }
                if let s = n.s { kv("Score at that inspection", "\(s) points (lower is better)") }
                if let c = n.c { kv("Critical violations cited", "\(c)") }
                if !n.pestNames.isEmpty { kv("Pests cited in the last year", n.pestNames.joined(separator: ", ")) }
                if let x = n.x { kv("Closed by the Health Department", Self.date(x)) }
                Text("Grades are the Health Department's own: A, B or C, posted at the restaurant (N = not yet graded, Z = grade pending, P = pending on re-opening). A grade comes from a graded inspection, so it can be older than the latest visit. Source: NYC Open Data, records through \(Self.date(model.recordsThrough?.nyc ?? "")).")
                    .font(.caption).foregroundStyle(Theme.muted)
                Link("Full inspection history on ABCEats", destination: Links.abcEats).font(.caption.weight(.semibold))
            }
        }
    }

    /// Counties outside NYC, Suffolk and Erie: NYSDOH's latest inspection. No official grade exists, and we don't make one.
    private func stateInspection(_ st: StateInspection) -> some View {
        section("Health inspections · New York State Department of Health", icon: "checkmark.shield") {
            VStack(alignment: .leading, spacing: 8) {
                kv("Latest inspection", Self.date(st.d))
                kv("Critical violations", st.nc > 0 ? "\(st.c) (\(st.nc) not corrected on the spot)" : "\(st.c)")
                kv("Other violations", "\(st.n)")
                if st.history.count > 1 {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Earlier inspections").font(.subheadline.weight(.semibold)).foregroundStyle(Theme.ink)
                        ForEach(st.history.dropLast().reversed(), id: \.date) { h in
                            Text("\(Self.date(h.date)) · \(h.critical) critical\(h.notCorrected > 0 ? " (\(h.notCorrected) not corrected)" : "") · \(h.other) other")
                                .font(.subheadline).foregroundStyle(Theme.ink2)
                        }
                    }
                }
                Text("There is no official grade outside New York City. NYSDOH: \u{201C}Any use of this data to develop a restaurant grading system is not supported or endorsed by the New York State Department of Health.\u{201D} Any analyses, interpretations or conclusions here are ours, not NYSDOH's. Source: health.data.ny.gov, records through \(Self.date(model.recordsThrough?.nysdoh ?? "")).")
                    .font(.caption).foregroundStyle(Theme.muted)
            }
        }
    }

    /// Suffolk County publishes only the violations its inspectors cited, one year at a time.
    private func suffolkViolations(_ sf: SuffolkViolations) -> some View {
        section("Health inspections · Suffolk County", icon: "checkmark.shield") {
            VStack(alignment: .leading, spacing: 8) {
                kv("Violations cited in 2025", "\(sf.n)")
                kv("Inspections that cited one", "\(sf.i)")
                if let d = sf.d { kv("Latest of those", Self.date(d)) }
                Text("Suffolk County's Department of Health Services publishes the violations its inspectors cited each year; there's no score or grade, and an inspection with no violations isn't listed. 2025 is the latest year published.")
                    .font(.caption).foregroundStyle(Theme.muted)
            }
        }
    }

    private var listing: some View {
        section("How we know it's here", icon: "mappin.and.ellipse") {
            VStack(alignment: .leading, spacing: 8) {
                kv("Listed as", place.handChecked && place.tier != .licensed ? "Hand-checked" : place.tier.label)
                if place.tier == .licensed { kv("Official list", place.jurisdiction.listName) }
                kv("Liquor license", place.liquorLicense ?? "— (none matched)")
                kv("County", place.county + (place.region.isEmpty ? "" : " · \(place.region)"))
                if let m = place.municipality { kv("Town or city", m) }
                if place.chainCount >= 2 { kv("Locations in New York", place.chainCount.formatted()) }
                Text(listingNote).font(.caption).foregroundStyle(Theme.muted)
            }
        }
    }

    private var listingNote: String {
        let checked = place.handChecked
        if place.source == "research" {
            return "On our hand-checked list (checked in October 2026 against a 2025 or 2026 source). The open map data didn't list it as a place to eat, so it's placed at its street address."
        }
        switch place.tier {
        case .licensed:
            return place.source == "official"
                ? "From the \(place.jurisdiction.listName). The open map data didn't have it, so it's placed at its street address."
                : "Matched to an active entry in the \(place.jurisdiction.listName)."
        case .confirmed where checked, .listing where checked:
            return "On our hand-checked list: checked open in October 2026 against a 2025 or 2026 source (its own site or menu, local news, or a tourism listing). It's in Overture's open map data too."
        case .confirmed, .listing:
            let rate = model.matchRate(for: place)
            let base = place.tier == .confirmed
                ? "A high-confidence listing in Overture's open map data."
                : "A single listing in Overture's open map data, so it may be closed or misfiled."
            let list = place.region == "New York City" ? "the NYC Health Department's permits" : "the state's food service permits"
            let measured = rate.map { " Checked against \(list), listings like this matched a permitted food business \($0) of the time." } ?? ""
            return base + measured + (checked ? " It's also on our hand-checked list, checked in October 2026 against a 2025 or 2026 source." : "")
        }
    }

    // MARK: helpers

    private var shareText: String {
        [place.name, place.fullAddress, "via \(Links.appName)", Links.site.absoluteString].filter { !$0.isEmpty }.joined(separator: "\n")
    }

    static func date(_ iso: String) -> String {
        let f = DateFormatter(); f.dateFormat = "yyyy-MM-dd"; f.locale = Locale(identifier: "en_US_POSIX")
        guard let d = f.date(from: iso) else { return iso }
        return d.formatted(date: .abbreviated, time: .omitted)
    }

    private func lines(_ s: String?, prefix: String) -> [String] {
        (s ?? "").components(separatedBy: "; ").filter { !$0.isEmpty }.map { prefix + $0 }
    }

    /// A section as a soft card: its label (with a small symbol), then its facts. Hand-checked research gets the gold card.
    private func section<Content: View>(_ title: String, icon: String, tint: Color = Theme.surface2, @ViewBuilder _ content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Label {
                Text(title.uppercased()).font(.caption.weight(.bold)).tracking(1)
            } icon: {
                Image(systemName: icon).font(.caption.weight(.bold))
            }
            .foregroundStyle(Theme.navy2)
            .accessibilityAddTraits(.isHeader)
            content()
        }
        .padding(16)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(RoundedRectangle(cornerRadius: 16).fill(tint))
    }

    private func fact(_ label: String, _ value: String) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(label).font(.subheadline.weight(.semibold)).foregroundStyle(Theme.ink)
            Text(value).font(.subheadline).foregroundStyle(Theme.ink2)
        }
    }

    @ViewBuilder
    private func kv(_ k: String, _ v: String?) -> some View {
        if let v {
            HStack(alignment: .firstTextBaseline) {
                Text(k).font(.subheadline).foregroundStyle(Theme.ink2)
                Spacer(minLength: 12)
                Text(v).font(.subheadline.weight(.semibold)).foregroundStyle(Theme.ink).multilineTextAlignment(.trailing)
            }
        }
    }
}

/// The glyph a place gets on the maps: pizza, bagels and delis, wings, hot dogs, dim sum, everything else.
enum MarkerGlyph {
    static func symbol(for p: Place) -> String {
        if !p.kinds.isDisjoint(with: [.slice, .buffaloPizza, .tomatoPie]) || p.tags.contains(.slice) { return "triangle.fill" }
        if !p.kinds.isDisjoint(with: [.bagel, .appetizing, .deli]) { return "circle.circle.fill" }
        if !p.kinds.isDisjoint(with: [.wings, .beefOnWeck]) { return "flame.fill" }
        if !p.kinds.isDisjoint(with: [.hots, .plate]) { return "takeoutbag.and.cup.and.straw.fill" }
        if p.kinds.contains(.dimSum) { return "basket.fill" }
        if p.michelin != nil { return "rosette" }
        return "fork.knife"
    }
}

extension String {
    var nonEmpty: String? { isEmpty ? nil : self }
}
