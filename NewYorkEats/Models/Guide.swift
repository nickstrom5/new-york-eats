import Foundation
import CoreLocation

/// The lists the app is built around. Each is a filter plus an order; none uses ratings (the app only publishes data it may).
enum Guide: String, CaseIterable, Identifiable, Hashable {
    case slices, bagels, wings, hots, upstate, dimSum, icons, oldest, nearMe, all

    var id: String { rawValue }

    var title: String {
        switch self {
        case .slices: "Slices & Pizza Styles"
        case .bagels: "Bagels, Delis & Appetizing"
        case .wings: "Wings & Beef on Weck"
        case .hots: "Hots & Plates"
        case .upstate: "Utica & Binghamton Classics"
        case .dimSum: "Dim Sum"
        case .icons: "New York Icons"
        case .oldest: "Oldest Places"
        case .nearMe: "Near Me"
        case .all: "All Restaurants"
        }
    }

    /// The Home card's title: short enough to sit on two lines of display type on the narrowest iPhone.
    var shortTitle: String {
        switch self {
        case .slices: "Slices"
        case .bagels: "Bagels & Delis"
        case .wings: "Wings & Weck"
        case .hots: "Hots & Plates"
        case .upstate: "Upstate Classics"
        case .dimSum: "Dim Sum"
        default: title
        }
    }

    var subtitle: String {
        switch self {
        case .slices: "NYC slice shops, Buffalo pies and Utica tomato pie"
        case .bagels: "Bagel bakeries, Jewish delis and smoked-fish counters"
        case .wings: "Buffalo's wing bars and roast beef on kummelweck"
        case .hots: "Rochester white hots, Plattsburgh michigans, Texas hots"
        case .upstate: "Chicken riggies, Utica greens, half-moons and spiedies"
        case .dimSum: "Chinatown, Flushing, Sunset Park and beyond"
        case .icons: "MICHELIN, James Beard honorees and institutions"
        case .oldest: "Years at the same address, oldest first"
        case .nearMe: "Everything around you, closest first"
        case .all: "Restaurants, cafés, bars and bakeries statewide"
        }
    }

    var systemImage: String {
        switch self {
        case .slices: "triangle"
        case .bagels: "circle.circle"
        case .wings: "flame"
        case .hots: "takeoutbag.and.cup.and.straw"
        case .upstate: "fork.knife.circle"
        case .dimSum: "basket"
        case .icons: "star.circle"
        case .oldest: "clock.arrow.circlepath"
        case .nearMe: "location"
        case .all: "fork.knife"
        }
    }

    /// The New York classics: hand-checked lists, highlighted on Home.
    var isClassic: Bool { [.slices, .bagels, .wings, .hots, .upstate, .dimSum].contains(self) }

    /// Guides whose order is a ranking worth numbering.
    var isRanked: Bool { [.icons, .oldest].contains(self) }

    var sortOptions: [SortOrder] {
        switch self {
        case .slices, .bagels, .wings, .hots, .upstate, .dimSum: [.featured, .nearest, .oldest, .name]
        case .icons: [.iconic, .oldest, .nearest]
        case .oldest: [.oldest]
        case .nearMe: [.nearest]
        case .all: [.name, .nearest]
        }
    }

    var defaultSort: SortOrder { sortOptions[0] }

    func includes(_ p: Place) -> Bool {
        switch self {
        // the classics promise "hand-checked", so only places our research confirmed open; a listing merely named "… Bagels" isn't enough
        case .slices: p.handChecked && !p.kinds.isDisjoint(with: [.slice, .buffaloPizza, .tomatoPie])
        case .bagels: p.handChecked && !p.kinds.isDisjoint(with: [.bagel, .deli, .appetizing])
        case .wings: p.handChecked && !p.kinds.isDisjoint(with: [.wings, .beefOnWeck])
        case .hots: p.handChecked && !p.kinds.isDisjoint(with: [.hots, .plate])
        case .upstate: p.handChecked && !p.kinds.isDisjoint(with: [.riggies, .greens, .halfMoon, .spiedie])
        case .dimSum: p.handChecked && p.kinds.contains(.dimSum)
        case .icons: p.iconicPoints != nil
        case .oldest: p.founded != nil && p.handChecked
        case .nearMe, .all: true
        }
    }
}

enum SortOrder: String, CaseIterable, Identifiable {
    case featured, nearest, oldest, name, iconic
    var id: String { rawValue }
    var label: String {
        switch self {
        case .featured: "Featured first"
        case .nearest: "Nearest"
        case .oldest: "Oldest first"
        case .name: "A to Z"
        case .iconic: "Most iconic"
        }
    }
}

/// Filters shared by every list. Search text lives with each list.
struct Filters: Equatable, Codable {
    var region: String?
    var town: String?
    var cuisine: String?
    var hideChains = false
    var confirmedOnly = false
    var includeNonRestaurants = false

    var activeCount: Int {
        [region != nil, town != nil, cuisine != nil, hideChains, confirmedOnly, includeNonRestaurants].filter { $0 }.count
    }

    func allows(_ p: Place) -> Bool {
        if !includeNonRestaurants && p.isVenue { return false }
        if let region, p.region != region { return false }
        if let town, p.city != town { return false }
        if let cuisine, p.cuisine != cuisine { return false }
        if hideChains && p.isChain { return false }
        if confirmedOnly && p.tier == .listing { return false }
        return true
    }
}

enum Ranking {
    /// `nameRank` (place id -> position in A-to-Z order, computed once at load) makes name order a number comparison.
    static func sort(_ places: [Place], by order: SortOrder, from here: CLLocation?, nameRank: [String: Int] = [:]) -> [Place] {
        func name(_ a: Place, _ b: Place) -> Bool {
            if let ra = nameRank[a.id], let rb = nameRank[b.id] { return ra < rb }
            return a.name.localizedCaseInsensitiveCompare(b.name) == .orderedAscending
        }
        switch order {
        case .nearest where here != nil:
            // distance computed once per place (a statewide list can hold 50,000 places)
            let d = Dictionary(places.map { ($0.id, $0.location?.distance(from: here!) ?? .greatestFiniteMagnitude) }, uniquingKeysWith: { a, _ in a })
            return places.sorted { d[$0.id]! != d[$1.id]! ? d[$0.id]! < d[$1.id]! : name($0, $1) }
        case .featured, .nearest:
            // honored places first, then the verified year at this address, then name
            return places.sorted {
                let a = $0.iconicPoints ?? -1, b = $1.iconicPoints ?? -1
                if a != b { return a > b }
                let fa = $0.founded ?? 9999, fb = $1.founded ?? 9999
                return fa != fb ? fa < fb : name($0, $1)
            }
        case .oldest:
            return places.sorted { ($0.founded ?? 9999, $0.name) < ($1.founded ?? 9999, $1.name) }
        case .name:
            return places.sorted(by: name)
        case .iconic:
            return places.sorted { ($0.iconicPoints ?? -1) != ($1.iconicPoints ?? -1) ? ($0.iconicPoints ?? -1) > ($1.iconicPoints ?? -1) : name($0, $1) }
        }
    }
}
