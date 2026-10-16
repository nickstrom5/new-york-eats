import Foundation
import CoreLocation

// MARK: - The bundled data (Resources/Data/index.json + places-<region>.json), written by pipeline/newyork.py with NY_APP=1

/// index.json: shared lookup tables, the region files and the data dates.
struct DataIndex: Decodable {
    let generated: String
    let overture_release: String
    let regions: [String]
    let counties: [String]
    let county_region: [Int]
    let cities: [String]
    let mailing: [String]
    let hoods: [String]
    let munis: [String]
    let cuisines: [String]
    let brands: [String]
    let srcs: [String]
    let liqt: [String?]
    let count_restaurants: Int
    let records_through: RecordsThrough
    /// match rates measured against the official lists (calibration.json "app"): area -> listing group -> rate
    let calibration: [String: [String: CalibrationGroup]]
    let files: [RegionFile]

    struct RecordsThrough: Decodable, Hashable {
        let nyc: String
        let nysdoh: String
        let suffolk: String
    }
    struct RegionFile: Decodable, Hashable {
        let region: String
        let file: String
        let count: Int
        let count_restaurants: Int
    }
}

struct CalibrationGroup: Decodable, Hashable {
    let n: Int
    let matched: Double
}

struct RegionData: Decodable {
    let region: String
    let places: [PlaceRecord]
}

/// NYC: the letter grade DOHMH posts at the door (official) with its date, and the latest inspection. Never computed from the score.
struct NYCInspection: Decodable, Hashable {
    /// A, B or C; N = not yet graded, Z = grade pending, P = pending on re-opening. nil when no grade is on file yet.
    let g: String?
    let gd: String?
    /// latest inspection date, its score (violation points: lower is better) and critical violations cited
    let d: String?
    let s: Int?
    let c: Int?
    /// pests cited in the last year: 04K rats, 04L mice, 04M roaches ("conditions conducive" is not counted)
    let p: String?
    /// latest date DOHMH closed the place
    let x: String?

    var gradeMeaning: String? {
        switch g {
        case "A": "Grade A"
        case "B": "Grade B"
        case "C": "Grade C"
        case "N": "Not yet graded"
        case "Z": "Grade pending"
        case "P": "Grade pending (re-opened)"
        default: nil
        }
    }
    var pestNames: [String] {
        (p ?? "").split(separator: ",").compactMap { ["04K": "rats", "04L": "mice", "04M": "roaches"][String($0)] }
    }
}

/// Counties outside NYC, Suffolk and Erie: NYSDOH's latest inspection and its counts. There is no official grade and we make none.
struct StateInspection: Decodable, Hashable {
    let d: String
    let c: Int
    let nc: Int
    let n: Int
    /// earlier inspections, oldest first: [date, critical, not corrected, non-critical]
    let h: [[Value]]?

    enum Value: Decodable, Hashable {
        case s(String), i(Int)
        init(from decoder: Decoder) throws {
            let c = try decoder.singleValueContainer()
            if let i = try? c.decode(Int.self) { self = .i(i) } else { self = .s(try c.decode(String.self)) }
        }
        var string: String { if case .s(let v) = self { v } else { "" } }
        var int: Int { if case .i(let v) = self { v } else { 0 } }
    }
    var history: [(date: String, critical: Int, notCorrected: Int, other: Int)] {
        (h ?? []).compactMap { r in r.count == 4 ? (r[0].string, r[1].int, r[2].int, r[3].int) : nil }
    }
}

/// Suffolk County: violations its inspectors cited in 2025 (no score, no grade; a clean inspection isn't on the list).
struct SuffolkViolations: Decodable, Hashable {
    let n: Int
    let i: Int
    let d: String?
}

struct PlaceRecord: Decodable {
    let id: String
    let n: String
    let c: Int?
    let co: Int
    let cu: Int
    let t: Int
    let s: Int
    let pl: Int?
    let hd: Int?
    let mu: Int?
    let a: String?
    let z: String?
    let la: Double?
    let lo: Double?
    let b: Int?
    let ch: Int?
    let j: Int?
    let v: Int?
    let bar: Int?
    let g: Int?
    let lq: Int?
    let nyc: NYCInspection?
    let st: StateInspection?
    let sf: SuffolkViolations?
    let hc: Int?
    let k: Int?
    let h: Int?
    let mi: Int?
    let ip: Double?
    let note: String?
    let jbf: String?
    let dish: String?
    let sea: String?
    let seas: Int?
    let br: String?
    let chef: String?
    let src: String?
    let fn: String?
    let f: Int?
    let w: String?
    let ph: String?
}

// MARK: - The model the views use

/// New York tags, from names and the hand-checked research (never from reviews). Bit order matches pipeline/newyork.py TAGS.
struct PlaceTags: OptionSet, Hashable {
    let rawValue: Int
    static let slice = PlaceTags(rawValue: 1)
    static let bagel = PlaceTags(rawValue: 2)
    static let deli = PlaceTags(rawValue: 4)
    static let wings = PlaceTags(rawValue: 8)
    static let weck = PlaceTags(rawValue: 16)
    static let hots = PlaceTags(rawValue: 32)
    static let dimSum = PlaceTags(rawValue: 64)
    static let upstate = PlaceTags(rawValue: 128)
    static let oldest = PlaceTags(rawValue: 256)
}

/// What the hand-checked research says a place is (data/research/README.md `kinds`; bit order = pipeline/newyork.py KINDS).
struct Kinds: OptionSet, Hashable {
    let rawValue: Int
    static let slice = Kinds(rawValue: 1)
    static let buffaloPizza = Kinds(rawValue: 2)
    static let tomatoPie = Kinds(rawValue: 4)
    static let bagel = Kinds(rawValue: 8)
    static let appetizing = Kinds(rawValue: 16)
    static let deli = Kinds(rawValue: 32)
    static let wings = Kinds(rawValue: 64)
    static let beefOnWeck = Kinds(rawValue: 128)
    static let hots = Kinds(rawValue: 256)
    static let plate = Kinds(rawValue: 512)
    static let riggies = Kinds(rawValue: 1024)
    static let greens = Kinds(rawValue: 2048)
    static let halfMoon = Kinds(rawValue: 4096)
    static let spiedie = Kinds(rawValue: 8192)
    static let dimSum = Kinds(rawValue: 16384)
    static let oldest = Kinds(rawValue: 32768)

    static let labels: [(Kinds, String)] = [(.slice, "Slices"), (.buffaloPizza, "Buffalo pizza"), (.tomatoPie, "Tomato pie"), (.bagel, "Bagels"),
                                            (.appetizing, "Appetizing"), (.deli, "Deli"), (.wings, "Wings"), (.beefOnWeck, "Beef on weck"),
                                            (.hots, "Hots"), (.plate, "Plates"), (.riggies, "Chicken riggies"), (.greens, "Utica greens"),
                                            (.halfMoon, "Half-moons"), (.spiedie, "Spiedies"), (.dimSum, "Dim sum"), (.oldest, "Historic")]
    var names: [String] { Kinds.labels.filter { contains($0.0) }.map(\.1) }
}

/// How a place got on the list. The share that matched a permitted business comes from calibration.json.
enum Tier: Int, Comparable {
    case listing = 0        // one map listing
    case confirmed = 1      // a high-confidence Meta listing, or a hand-checked place
    case licensed = 2       // on an official list: a DOHMH or NYSDOH permit, a Suffolk inspection, a Buffalo or liquor license

    static func < (a: Tier, b: Tier) -> Bool { a.rawValue < b.rawValue }

    var label: String {
        switch self {
        case .licensed: "On an official list"
        case .confirmed: "High-confidence listing"   // the family wording (Nick, 2026-10-13); these matched a permit far more often than single listings
        case .listing: "Listing only"
        }
    }
}

enum Jurisdiction: Int {
    case none = 0, dohmh = 1, nysdoh = 2, suffolk = 3, buffalo = 4, sla = 5
    var listName: String {
        switch self {
        case .dohmh: "NYC Health Department (DOHMH) restaurant permits"
        case .nysdoh: "New York State Department of Health food service permits"
        case .suffolk: "Suffolk County Department of Health Services inspections"
        case .buffalo: "City of Buffalo restaurant licenses"
        case .sla: "New York State Liquor Authority licenses"
        case .none: ""
        }
    }
}

enum MichelinDistinction: Int {
    case recommended = 1, bib = 2, oneStar = 3, twoStars = 4, threeStars = 5
    /// Honors are facts, written out: never a row of stars that reads like a rating.
    var label: String {
        switch self {
        case .recommended: "MICHELIN Guide"
        case .bib: "Bib Gourmand"
        case .oneStar: "1 MICHELIN Star"
        case .twoStars: "2 MICHELIN Stars"
        case .threeStars: "3 MICHELIN Stars"
        }
    }
}

struct Place: Identifiable, Hashable {
    let id: String
    let name: String
    let address: String?
    /// the borough in NYC; elsewhere the city, village or hamlet in the mailing address
    let city: String?
    /// the mailing name when it isn't the city shown (a Queens postal name like Flushing is kept for search)
    let mailingName: String?
    /// NYC neighborhood (NTA 2020)
    let neighborhood: String?
    /// the town or city government outside NYC, when it isn't the mailing name (Levittown is in the Town of Hempstead)
    let municipality: String?
    let county: String
    let region: String
    let zip: String?
    let coordinate: CLLocationCoordinate2D?
    let cuisine: String
    let brand: String?
    let chainCount: Int
    let tier: Tier
    let jurisdiction: Jurisdiction
    let liquorLicense: String?
    let source: String
    let isVenue: Bool
    let isBar: Bool
    let tags: PlaceTags
    /// On our hand-checked list (data/research): confirmed open with a 2025–26 source.
    let handChecked: Bool
    let kinds: Kinds
    let honorFlags: Int
    let michelin: MichelinDistinction?
    let iconicPoints: Double?
    let note: String?
    let jamesBeard: String?
    let dishes: String?
    let season: String?
    let isSeasonal: Bool
    let branchOf: String?
    let chef: String?
    let sourceURL: URL?
    let foundedNote: String?
    let founded: Int?
    let website: URL?
    let phone: String?
    let nyc: NYCInspection?
    let stateInspection: StateInspection?
    let suffolk: SuffolkViolations?
    /// normalized text for search: name, places, zip, cuisine, brand, dishes, then the address with street words abbreviated
    let searchText: String
    let nameText: String

    static func == (a: Place, b: Place) -> Bool { a.id == b.id }
    func hash(into h: inout Hasher) { h.combine(id) }

    var isHonored: Bool { handChecked }
    var isChain: Bool { chainCount >= 5 }
    var jamesBeardLabel: String? {
        if honorFlags & 1 != 0 { return "America's Classic" }
        if honorFlags & 2 != 0 { return "James Beard winner" }
        if honorFlags & 4 != 0 { return "James Beard nominee" }
        if honorFlags & 8 != 0 { return "James Beard semifinalist" }
        return nil
    }
    /// "Flushing, Queens", "Williamsburg, Brooklyn" or "Levittown"
    var placeName: String? {
        guard let city else { return mailingName }
        if let n = neighborhood ?? mailingName, n != city { return "\(n), \(city)" }
        return city
    }
    var townLine: String { [placeName, cuisine].compactMap { $0 }.joined(separator: " · ") }
    var fullAddress: String {
        let town = (region == "New York City" ? (mailingName ?? (city == "Manhattan" ? "New York" : city)) : (mailingName ?? city))
        return [address, [town.map { "\($0), NY" }, zip].compactMap { $0 }.joined(separator: " ")].compactMap { $0 }.filter { !$0.isEmpty }.joined(separator: ", ")
    }
    var location: CLLocation? { coordinate.map { CLLocation(latitude: $0.latitude, longitude: $0.longitude) } }

    init(_ r: PlaceRecord, index ix: DataIndex) {
        func at(_ list: [String], _ i: Int?) -> String? { i.flatMap { $0 >= 0 && $0 < list.count ? list[$0] : nil } }
        let city = at(ix.cities, r.c)
        let mailing = at(ix.mailing, r.pl)
        let hood = at(ix.hoods, r.hd)
        let muni = at(ix.munis, r.mu)
        let county = at(ix.counties, r.co) ?? ""
        let region = r.co < ix.county_region.count ? (at(ix.regions, ix.county_region[r.co]) ?? "") : ""
        let cuisine = at(ix.cuisines, r.cu) ?? "American & Other"
        let brand = at(ix.brands, r.b)
        id = r.id
        name = r.n
        address = r.a
        self.city = city
        mailingName = mailing
        neighborhood = hood
        municipality = muni
        self.county = county
        self.region = region
        zip = r.z
        if let la = r.la, let lo = r.lo { coordinate = CLLocationCoordinate2D(latitude: la, longitude: lo) } else { coordinate = nil }
        self.cuisine = cuisine
        self.brand = brand
        chainCount = r.ch ?? 1
        tier = Tier(rawValue: r.t) ?? .listing
        jurisdiction = Jurisdiction(rawValue: r.j ?? 0) ?? .none
        liquorLicense = r.lq.flatMap { $0 > 0 && $0 < ix.liqt.count ? ix.liqt[$0] : nil }
        source = r.s < ix.srcs.count ? ix.srcs[r.s] : "meta"
        isVenue = r.v == 1
        isBar = r.bar == 1
        tags = PlaceTags(rawValue: r.g ?? 0)
        handChecked = r.hc == 1
        kinds = Kinds(rawValue: r.k ?? 0)
        honorFlags = r.h ?? 0
        michelin = r.mi.flatMap(MichelinDistinction.init(rawValue:))
        iconicPoints = r.ip
        note = r.note
        jamesBeard = r.jbf
        dishes = r.dish
        season = r.sea
        isSeasonal = r.seas == 1
        branchOf = r.br
        chef = r.chef
        sourceURL = r.src.flatMap { URL(string: $0) }
        foundedNote = r.fn
        founded = r.f
        website = r.w.flatMap { URL(string: $0.hasPrefix("http") ? $0 : "https://" + $0) }
        phone = r.ph
        nyc = r.nyc
        stateInspection = r.st
        suffolk = r.sf
        // what people search for: the name, the borough or city, the neighborhood, the mailing name, the town, dishes
        searchText = " " + Search.normalize([r.n, city, mailing, hood, muni, r.z, cuisine, brand, r.dish].compactMap { $0 }.joined(separator: " ")) + " "
            + Search.normalizeAddress(r.a ?? "") + " "
        nameText = " " + Search.normalize([r.n, brand].compactMap { $0 }.joined(separator: " ")) + " "
    }
}
