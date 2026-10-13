import XCTest
import CoreLocation
@testable import NewYorkEats

@MainActor
final class NewYorkEatsTests: XCTestCase {

    /// A tiny data folder with the same shape as Resources/Data (index.json + one file per region).
    private func sampleModel() async throws -> AppModel {
        let index = """
        {"v":1,"generated":"2026-10-07","overture_release":"2026-09-23.1",
         "regions":["New York City","Western New York","Mohawk Valley","Long Island"],"slugs":["new-york-city","western-new-york","mohawk-valley","long-island"],
         "counties":["New York","Kings","Erie","Oneida","Nassau","Suffolk","Queens"],"county_region":[0,0,1,2,3,3,0],
         "cities":["Manhattan","Brooklyn","Buffalo","Utica","Levittown","Hampton Bays","Queens"],"mailing":["Flushing"],"hoods":["Lower East Side","Chinatown","Bensonhurst"],
         "munis":["Hempstead"],"cuisines":["Jewish & Kosher","Pizza","Chinese","Chicken & Wings","Italian","American & Other","Coffee & Café"],
         "brands":["Dunkin'"],"srcs":["official","meta","AllThePlaces","DAC","research"],"liqt":[null,"Restaurant"],
         "count":9,"count_restaurants":8,"records_through":{"nyc":"2026-09-29","nysdoh":"2026-09-24","suffolk":"2025-12-31"},
         "calibration":{"nyc_dohmh":{"Meta, confidence 0.95+":{"n":17574,"matched":0.822}},"state_nysdoh":{"Meta, confidence 0.95+":{"n":15832,"matched":0.456}}},
         "files":[{"region":"New York City","file":"places-new-york-city.json","count":5,"count_restaurants":5},
                  {"region":"Upstate","file":"places-upstate.json","count":4,"count_restaurants":3}]}
        """
        let nyc = """
        {"region":"New York City","places":[
          {"id":"a","n":"Katz's Delicatessen","c":0,"co":0,"cu":0,"t":2,"s":0,"j":1,"hd":0,"hc":1,"k":32,"g":4,"h":0,"ip":80,"a":"205 E Houston St","z":"10002",
           "la":40.7223,"lo":-73.9874,"dish":"pastrami on rye","nyc":{"g":"A","gd":"2026-05-02","d":"2026-05-02","s":9,"c":1}},
          {"id":"b","n":"Joe's Pizza","c":0,"co":0,"cu":1,"t":2,"s":0,"j":1,"hc":1,"k":1,"g":1,"ip":40,"a":"7 Carmine St","z":"10014","la":40.7305,"lo":-74.0021,
           "nyc":{"g":"A","gd":"2026-03-10","d":"2026-03-10","s":5,"c":0}},
          {"id":"c","n":"Nom Wah Tea Parlor","c":0,"co":0,"cu":2,"t":2,"s":0,"j":1,"hd":1,"hc":1,"k":16384,"g":64,"f":1968,"a":"13 Doyers St","la":40.7142,"lo":-73.9982,
           "nyc":{"g":"B","gd":"2026-07-01","d":"2026-07-01","s":18,"c":2,"p":"04L"}},
          {"id":"d","n":"Asian Jewels","c":6,"co":6,"cu":2,"t":1,"s":1,"pl":0,"hc":1,"k":16384,"g":64,"a":"133-30 39th Ave","la":40.7590,"lo":-73.8330},
          {"id":"e","n":"Dunkin'","c":1,"co":1,"cu":6,"t":1,"s":2,"b":0,"ch":400,"hd":2,"la":40.6110,"lo":-73.9970}
        ]}
        """
        let upstate = """
        {"region":"Upstate","places":[
          {"id":"f","n":"Anchor Bar","c":2,"co":2,"cu":3,"t":1,"s":1,"hc":1,"k":192,"g":24,"a":"1047 Main St","la":42.9002,"lo":-78.8695},
          {"id":"g","n":"Chesterfield's Tavolo","c":3,"co":3,"cu":4,"t":2,"s":0,"j":2,"hc":1,"k":2048,"g":128,"a":"1713 Bleecker St","la":43.0950,"lo":-75.2160,
           "st":{"d":"2026-06-11","c":1,"nc":0,"n":3,"h":[["2025-06-02",0,0,2],["2026-06-11",1,0,3]]}},
          {"id":"h","n":"Levittown Bagels","c":4,"co":4,"cu":5,"t":0,"s":1,"mu":0,"g":2,"a":"3000 Hempstead Tpke","la":40.7240,"lo":-73.5150},
          {"id":"i","n":"Stewart's Shops","c":5,"co":5,"cu":5,"t":1,"s":1,"v":1,"la":40.87,"lo":-72.52,"sf":{"n":4,"i":2,"d":"2025-08-14"}}
        ]}
        """
        let dir = FileManager.default.temporaryDirectory.appendingPathComponent("ny-test-\(UUID().uuidString)")
        try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        try index.data(using: .utf8)!.write(to: dir.appendingPathComponent("index.json"))
        try nyc.data(using: .utf8)!.write(to: dir.appendingPathComponent("places-new-york-city.json"))
        try upstate.data(using: .utf8)!.write(to: dir.appendingPathComponent("places-upstate.json"))
        let model = AppModel(defaults: UserDefaults(suiteName: "test-\(UUID().uuidString)")!)
        await model.load(from: dir)
        XCTAssertTrue(model.isLoaded, model.loadError ?? "")
        return model
    }

    func testDecodesRegionFilesAndHidesNonRestaurants() async throws {
        let m = try await sampleModel()
        XCTAssertEqual(m.places.count, 9)
        XCTAssertEqual(m.place(id: "f")?.region, "Western New York")
        XCTAssertEqual(m.place(id: "a")?.county, "New York")
        let all = m.list(.all, sort: .name, search: "", here: nil)
        XCTAssertFalse(all.contains { $0.id == "i" }, "a convenience-store counter is hidden unless asked for")
        m.filters.includeNonRestaurants = true
        XCTAssertTrue(m.list(.all, sort: .name, search: "", here: nil).contains { $0.id == "i" })
    }

    func testGuidesListOnlyHandCheckedPlaces() async throws {
        let m = try await sampleModel()
        XCTAssertEqual(m.list(.slices, sort: .name, search: "", here: nil).map(\.id), ["b"])
        XCTAssertEqual(m.list(.bagels, sort: .name, search: "", here: nil).map(\.id), ["a"],
                       "a listing merely named \u{201C}Bagels\u{201D} stays out of the checked guide")
        XCTAssertEqual(m.list(.all, sort: .name, search: "levittown bagels", here: nil).map(\.id), ["h"], "but it's still in the directory")
        XCTAssertEqual(Set(m.list(.dimSum, sort: .name, search: "", here: nil).map(\.id)), ["c", "d"])
        XCTAssertEqual(m.list(.wings, sort: .name, search: "", here: nil).map(\.id), ["f"], "wings and beef on weck share a guide")
        XCTAssertEqual(m.list(.upstate, sort: .name, search: "", here: nil).map(\.id), ["g"])
        XCTAssertEqual(m.list(.icons, sort: .iconic, search: "", here: nil).first?.id, "a")
        XCTAssertEqual(m.list(.nearMe, sort: .nearest, search: "", here: nil), [], "near me needs a location")
    }

    func testBoroughsNeighborhoodsAndTowns() async throws {
        let m = try await sampleModel()
        func ids(_ q: String) -> Set<String> { Set(m.list(.all, sort: .name, search: q, here: nil).map(\.id)) }
        XCTAssertEqual(ids("flushing"), ["d"], "a Queens postal name narrows to its places")
        XCTAssertEqual(ids("chinatown"), ["c"], "an NYC neighborhood narrows to its places")
        XCTAssertEqual(ids("buffalo"), ["f"])
        XCTAssertEqual(ids("hempstead"), ["h"], "the town government finds its hamlets")
        XCTAssertEqual(m.place(id: "a")?.placeName, "Lower East Side, Manhattan")
        XCTAssertEqual(m.place(id: "a")?.fullAddress, "205 E Houston St, New York, NY 10002")
    }

    func testSearchTagsDishesAndStreets() async throws {
        let m = try await sampleModel()
        func ids(_ q: String) -> [String] { m.list(.all, sort: .name, search: q, here: nil).map(\.id) }
        XCTAssertEqual(Set(ids("dim sum")), ["c", "d"])
        XCTAssertEqual(ids("pastrami"), ["a"], "a dish is searchable")
        XCTAssertEqual(ids("katzs"), ["a"], "\u{201C}Katz's\u{201D} without the apostrophe")
        XCTAssertEqual(ids("atz"), [], "matches the start of words only")
        XCTAssertEqual(ids("carmine street"), ["b"], "street words match the abbreviated address")
        XCTAssertEqual(ids("beef on weck"), ["f"])
        XCTAssertEqual(ids("dim sum in flushing"), ["d"], "a stop word after a guide and a place isn't a search word")
        XCTAssertEqual(ids("dim sum near me"), ids("dim sum"), "\u{201C}near me\u{201D} asks for nothing")
        XCTAssertEqual(ids("hempstead tpke"), ["h"], "a town followed by a street type is a street")
        XCTAssertEqual(Search.normalizeAddress("NY-25A Main St"), "rt 25a main st", "route spellings read the same")
        XCTAssertEqual(ids("🍕"), [], "nothing searchable typed means no results, not everything")
        XCTAssertEqual(ids("!!! ?"), [])
    }

    /// Typing narrows from the previous result, but never across a change of meaning ("bage" is a word, "bagel" is the guide).
    func testIncrementalSearchKeepsGuideMatches() async throws {
        let m = try await sampleModel()
        _ = m.list(.all, sort: .name, search: "bage", here: nil)
        XCTAssertEqual(Set(m.list(.all, sort: .name, search: "bagel", here: nil).map(\.id)), ["h"], "only the bagel-tagged place in the sample")
        _ = m.list(.all, sort: .name, search: "ka", here: nil)
        XCTAssertEqual(m.list(.all, sort: .name, search: "katz", here: nil).map(\.id), ["a"])
        XCTAssertEqual(m.list(.all, sort: .name, search: "k", here: nil).map(\.id).contains("a"), true, "a shorter search widens again")
    }

    func testNearestSort() async throws {
        let m = try await sampleModel()
        let washSq = CLLocation(latitude: 40.7308, longitude: -73.9973)
        XCTAssertEqual(m.list(.nearMe, sort: .nearest, search: "", here: washSq).first?.id, "b", "Joe's on Carmine St is closest to Washington Square")
    }

    func testOfficialRecordsStayWithTheirJurisdiction() async throws {
        let m = try await sampleModel()
        let katz = m.place(id: "a")!
        XCTAssertEqual(katz.nyc?.g, "A")
        XCTAssertEqual(katz.nyc?.gradeMeaning, "Grade A")
        XCTAssertNil(katz.stateInspection, "an NYC place has no state inspection")
        XCTAssertEqual(m.place(id: "c")?.nyc?.pestNames, ["mice"])
        let utica = m.place(id: "g")!
        XCTAssertNil(utica.nyc, "no letter grade outside NYC")
        XCTAssertEqual(utica.stateInspection?.c, 1)
        XCTAssertEqual(utica.stateInspection?.history.count, 2)
        XCTAssertEqual(m.place(id: "i")?.suffolk?.n, 4)
        XCTAssertEqual(m.recordsThrough?.nyc, "2026-09-29")
    }

    func testFiltersSavedPlacesAndLabels() async throws {
        let m = try await sampleModel()
        m.filters.hideChains = true
        XCTAssertFalse(m.list(.all, sort: .name, search: "", here: nil).contains { $0.name == "Dunkin'" })
        m.filters = Filters(confirmedOnly: true)
        XCTAssertFalse(m.list(.all, sort: .name, search: "", here: nil).contains { $0.id == "h" }, "single listings drop out")
        m.filters = Filters(region: "New York City")
        XCTAssertEqual(Set(m.list(.all, sort: .name, search: "", here: nil).map(\.id)), ["a", "b", "c", "d", "e"])
        m.filters = Filters(town: "Manhattan")
        XCTAssertEqual(Set(m.list(.all, sort: .name, search: "", here: nil).map(\.id)), ["a", "b", "c"])
        let p = m.place(id: "b")!
        m.toggleSaved(p)
        XCTAssertEqual(m.savedPlaces.map(\.id), ["b"])
        m.toggleSaved(p)
        XCTAssertTrue(m.savedPlaces.isEmpty)
        XCTAssertEqual(m.matchRate(for: m.place(id: "f")!), "46%", "upstate listings cite the state list's rate")
        XCTAssertNil(m.matchRate(for: m.place(id: "a")!), "permitted places don't cite a listing rate")
        XCTAssertEqual(PlaceDetailView.date("2026-04-29").isEmpty, false)
    }

    /// The real bundled data decodes and holds the guides the app promises.
    func testBundledData() async throws {
        let m = AppModel(defaults: UserDefaults(suiteName: "bundle-\(UUID().uuidString)")!)
        await m.load()
        XCTAssertTrue(m.isLoaded, m.loadError ?? "")
        XCTAssertGreaterThan(m.restaurantCount, 40_000)
        XCTAssertEqual(m.places.filter { !$0.isVenue }.count, m.restaurantCount, "every file in index.json loaded (NYC is five borough files)")
        XCTAssertGreaterThan(m.places.filter { $0.region == "New York City" }.count, 25_000)
        XCTAssertEqual(m.regions.count, 10)
        XCTAssertGreaterThan(m.count(.slices), 15)
        XCTAssertGreaterThan(m.count(.bagels), 25)
        XCTAssertGreaterThan(m.count(.wings), 12)
        XCTAssertGreaterThan(m.count(.icons), 150)
        XCTAssertEqual(Set(m.places.map(\.id)).count, m.places.count, "ids are unique")
        XCTAssertTrue(m.places.contains { $0.name.hasPrefix("Katz's") && $0.city == "Manhattan" && $0.handChecked })
        XCTAssertFalse(m.places.contains { $0.name.range(of: #"gentlem[ae]n'?s club|strip club|exotic dancer"#, options: [.regularExpression, .caseInsensitive]) != nil },
                       "adult clubs aren't restaurants")
        XCTAssertFalse(m.places.contains { ($0.website?.absoluteString ?? "").range(
            of: #"yelp\.com|business\.site|google\.com|groupon\.com|yellowpages\.com"#, options: .regularExpression) != nil },
                       "directory links were checked out")
        XCTAssertTrue(m.places.allSatisfy { $0.nyc == nil || $0.region == "New York City" }, "NYC grades only in the five boroughs")
        XCTAssertTrue(m.places.allSatisfy { $0.nyc?.g == nil || $0.nyc?.gd != nil }, "an official grade always shows its date")
        XCTAssertTrue(m.places.allSatisfy { $0.stateInspection == nil || !["New York City"].contains($0.region) }, "no state inspections inside NYC")
        XCTAssertTrue(m.places.allSatisfy { $0.suffolk == nil || $0.county == "Suffolk" })
        XCTAssertTrue(m.places.allSatisfy { $0.phone == nil || $0.phone!.range(of: #"^\+1\d{10}$"#, options: .regularExpression) != nil }, "phones are +1 and ten digits")
    }
}
