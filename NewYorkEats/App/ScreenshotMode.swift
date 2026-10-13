import Foundation
import CoreLocation
import UIKit

/// `-screenshot <name>` opens one screen with fixed state for App Store screenshots (scripts/capture-screenshots.sh).
/// Names: home, slices, bagels, wings, detail, map, icons, saved, about.
enum ScreenshotMode {
    /// Debug builds only: an App Store build ignores the launch argument, so no one can reach seeded screens or fake locations.
    static var name: String? {
        #if DEBUG
        let args = ProcessInfo.processInfo.arguments
        guard let i = args.firstIndex(of: "-screenshot"), i + 1 < args.count else { return nil }
        return args[i + 1]
        #else
        return nil
        #endif
    }
    static var isActive: Bool { name != nil }

    @MainActor
    static func apply(to model: AppModel) {
        guard let name, model.isLoaded else { return }
        model.filters = Filters()
        // Washington Square Park, so "nearest" lists have distances without a permission prompt
        model.screenshotLocation = CLLocation(latitude: 40.7308, longitude: -73.9973)
        // the first hand-checked place with this name (a branch never stands in for the original)
        let named = { (p: Place, n: String) in p.name.lowercased().hasPrefix(n.lowercased()) }
        let pick = { (n: String) in model.places.first { named($0, n) && $0.handChecked && $0.branchOf == nil } ?? model.places.first { named($0, n) } }
        for n in ["Katz's Delicatessen", "Joe's Pizza", "Anchor Bar", "Nom Wah Tea Parlor"] {
            if let p = pick(n), !model.isSaved(p) { model.toggleSaved(p) }
        }
        let open = { (g: Guide) in model.tab = .guides; model.selectedGuide = g; model.guidesPath = [.guide(g)] }
        switch name {
        case "slices": open(.slices)
        case "bagels": open(.bagels)
        case "wings":   // Buffalo's wings from downtown Buffalo (Niagara Square), not 285 miles from Manhattan
            model.screenshotLocation = CLLocation(latitude: 42.8864, longitude: -78.8784)
            open(.wings)
        case "icons": open(.icons)
        case "detail":
            open(.bagels)
            if let p = pick("Katz's Delicatessen") ?? model.places.first { model.selectedPlace = p; model.guidesPath.append(.place(p)) }
        case "map": model.tab = .map
        case "saved": model.tab = .saved
        case "about": model.tab = .about
        default: model.tab = .guides; model.selectedGuide = nil
        }
        // iPad shows the place column next to every list, so give each shot a place instead of "Pick a place".
        guard UIDevice.current.userInterfaceIdiom == .pad, model.selectedPlace == nil else { return }
        let place: Place? = switch name {
        case "slices": pick("Joe's Pizza")
        case "wings": pick("Anchor Bar")
        case "icons": pick("Katz's Delicatessen")
        case "saved": pick("Nom Wah Tea Parlor")
        case "about": nil
        case "map": pick("Joe's Pizza")
        default: pick("Katz's Delicatessen")
        }
        model.selectedPlace = place
    }
}
