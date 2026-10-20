import Foundation

/// The app's web pages and support address, in one place.
/// The site is GitHub Pages. Until the newyork.eatsranked.com DNS record exists, links use the github.io address; once it resolves
/// (dig shows the CNAME) and Pages serves it, switch these with scripts/make-site.py's CUSTOM_DOMAIN. GitHub forwards the old
/// address, so builds that shipped with it keep working.
enum Links {
    static let appName = "New York Eats"
    static let base = "https://newyork.eatsranked.com"
    static let site = URL(string: base + "/")!
    static let privacy = URL(string: base + "/privacy.html")!
    static let terms = URL(string: base + "/terms.html")!
    static let supportEmail = "nick@eatsranked.com"
    /// the NYC Health Department's own restaurant grade lookup (linked, never scraped)
    static let abcEats = URL(string: "https://a816-health.nyc.gov/ABCEatsRestaurants/")!

    static var correctionEmail: URL {
        URL(string: "mailto:\(supportEmail)?subject=New%20York%20Eats%20correction")!
    }
}
