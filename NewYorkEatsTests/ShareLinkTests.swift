import XCTest
@testable import NewYorkEats

/// Share sends the place's page on the Eats Ranked site, not a map listing (Nick, 2026-10-22: "can the share button on the eats
/// ranked restaurant page link to the eats ranked page, not the maps listing").
@MainActor
final class ShareLinkTests: XCTestCase {

    private func bundledModel() async throws -> AppModel {
        let m = AppModel(defaults: UserDefaults(suiteName: "share-\(UUID().uuidString)")!)
        await m.load()
        XCTAssertTrue(m.isLoaded, m.loadError ?? "")
        return m
    }

    /// The ids the live web app can open from a shared link: the detail-<region>.json files findPlace looks a shared #p= id up in, read from the repo's docs/data.
    private func webIDs() throws -> Set<String> {
        let data = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().appendingPathComponent("docs/data")
        let files = try FileManager.default.contentsOfDirectory(at: data, includingPropertiesForKeys: nil).filter { $0.lastPathComponent.hasPrefix("detail-") }
        XCTAssertEqual(files.count, 10, "one detail file per region")
        var ids = Set<String>()
        for f in files {
            let file = try XCTUnwrap(JSONSerialization.jsonObject(with: Data(contentsOf: f)) as? [String: Any])
            ids.formUnion(try XCTUnwrap(file["ids"] as? [String]))
        }
        return ids
    }

    /// The link is the web app's place URL on the live domain, and the message names the place and the app. No Apple Maps or
    /// Google link anywhere, and no street address (Messages makes a Maps link of one).
    func testShareSendsTheEatsRankedPlacePage() async throws {
        let m = try await bundledModel()
        let web = try webIDs()
        let p = try XCTUnwrap(m.places.first { web.contains($0.id) && $0.city != nil && $0.address != nil })
        XCTAssertEqual(Links.explore.absoluteString, "https://newyork.eatsranked.com/explore/")
        XCTAssertEqual(Links.share(p).absoluteString, "https://newyork.eatsranked.com/explore/#p=" + p.id)
        XCTAssertEqual(Links.shareMessage(p), "\(p.name), \(p.city!), on New York Eats")
        for place in m.places.prefix(500) + [p] {
            let url = Links.share(place), sent = url.absoluteString + "\n" + Links.shareMessage(place)
            XCTAssertEqual(url.scheme, "https")
            XCTAssertEqual(url.host(), "newyork.eatsranked.com", sent)
            XCTAssertTrue(url.path().hasPrefix(Links.explore.path()), sent)
            for maps in ["maps.apple.com", "maps.google", "google.com", "goo.gl", "maps.app"] {
                XCTAssertFalse(sent.contains(maps), "Share sends a map link (\(maps)): \(sent)")
            }
            if let street = place.address, !street.isEmpty, !place.name.contains(street), !(place.city ?? "").contains(street) {
                XCTAssertFalse(sent.contains(street), "the street address goes out: \(sent)")
            }
        }
    }

    /// Every place's link opens it in the web app: a place the web app has gets explore/#p=<its id>, the id the web app uses, and
    /// a place it leaves out gets the web app's front page, never a #p= link that opens nothing.
    func testEveryShareLinkOpensInTheWebApp() async throws {
        let m = try await bundledModel()
        let web = try webIDs()
        XCTAssertGreaterThan(web.count, m.places.count / 2, "the web data wasn't read")
        var wrong: [String] = []
        for p in m.places {
            let want = web.contains(p.id) ? Links.explore.absoluteString + "#p=" + p.id : Links.explore.absoluteString
            if Links.share(p).absoluteString != want { wrong.append("\(p.name) (\(p.id)): \(Links.share(p).absoluteString)") }
        }
        XCTAssertEqual(wrong.count, 0, "links that don't open the place: " + wrong.prefix(5).joined(separator: "; "))
        XCTAssertGreaterThan(m.places.filter { web.contains($0.id) }.count, m.places.count * 9 / 10, "most places have a page")
    }
}
