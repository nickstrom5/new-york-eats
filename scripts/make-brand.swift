// Regenerates the brand images: the app icon (a flat everything bagel on state-flag blue; Nick's pick, Oct 7, 2026; redrawn
// Oct 9, 2026 in the shared Eats Ranked flat style Nick approved, ../state-prompts/ICON-STYLE.md: same food and colours),
// docs/brand/, and the site's og.png, favicons and manifest icons.
// Usage: swift scripts/make-brand.swift   (run from ny-eats/)
//        swift scripts/make-brand.swift og ["<tagline>"]   redraws docs/og.png only, never the icons. scripts/make-site.py runs
//        this whenever the restaurant or town count changes; without a tagline it reads og_line from playbook/site-numbers.json.
import AppKit
import CoreGraphics

let root = FileManager.default.currentDirectoryPath
func rgb(_ hex: UInt32, _ a: CGFloat = 1) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 0xFF) / 255, green: CGFloat((hex >> 8) & 0xFF) / 255, blue: CGFloat(hex & 0xFF) / 255, alpha: a)
}
let blue = rgb(0x14325C), gold = rgb(0xE0A526), white = rgb(0xFFFFFF)

func canvas(_ w: Int, _ h: Int, _ draw: (CGContext) -> Void) -> CGImage {
    let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0,
                        space: CGColorSpace(name: CGColorSpace.sRGB)!, bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    ctx.setShouldAntialias(true); ctx.interpolationQuality = .high
    draw(ctx)
    return ctx.makeImage()!
}
func save(_ img: CGImage, _ path: String) {
    let url = URL(fileURLWithPath: root + "/" + path)
    try? FileManager.default.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
    try! NSBitmapImageRep(cgImage: img).representation(using: .png, properties: [:])!.write(to: url)
    print("wrote", path)
}

// ---- the app icon's food: a flat everything bagel from above (the hole shows the blue ground). Eats Ranked flat style, Oct 9, 2026
/// Where every part of the bagel goes inside an s x s square at the origin, CG y-up. Design units are px at 1024.
/// Seeds are (centre, rotation in radians, isSesame).
func bagelLayout(_ s: CGFloat) -> (outer: CGRect, under: CGRect, crown: CGRect, rim: CGRect, hole: CGRect, holeFloor: CGRect,
                                    seeds: [(CGPoint, CGFloat, Bool)]) {
    let k = s / 1024
    let cx = s * 0.5, cy = s * 0.5 - 9 * k             // centre of the ring, a touch low like the references
    let lift = 24 * k                                  // the crown, rim and hole sit this far up: the top of a puffed
                                                       // loaf seen a little from the front, so more crust shows below
    let drop = 18 * k                                  // how far the underside shows below the outer slope
    func oval(_ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat) -> CGRect {
        CGRect(x: x - w * k / 2, y: y - h * k / 2, width: w * k, height: h * k)
    }
    let outer = oval(cx, cy, 717, 676)                 // 0.700 x 0.660 of the canvas
    let crown = oval(cx, cy + lift, 538, 486)          // 0.525 x 0.475: crust band ~72 px at the top, ~120 px at the bottom
    let rim = oval(cx, cy + lift, 282, 244)            // where the dough rolls down into the hole (28 px band, 24 at top/bottom)
    let hole = oval(cx, cy + lift, 226, 196)           // the hole's opening on the top, 0.22 x 0.19
    // Seeds, hand-placed (no randomness): angle round the ring in degrees (0 = right, 90 = up), how far across the crown
    // from the rim (0) to the crown's outer edge (1), sesame or poppy. Sesame lies along the ring's tangent. Light and
    // dark alternate round the ring so the mix reads as everything seasoning. Poppies sit where the crown band is widest
    // (towards the sides), sesame can sit anywhere; every seed keeps 40 px or more clear of both crown edges.
    let table: [(CGFloat, CGFloat, Bool)] = [
        (10, 0.50, false), (56, 0.48, true), (102, 0.52, true), (152, 0.50, false),
        (196, 0.52, true), (222, 0.50, false), (274, 0.50, true), (328, 0.50, false),
    ]
    let seeds: [(CGPoint, CGFloat, Bool)] = table.map { deg, f, sesame in
        let t = deg * .pi / 180
        let rx = rim.width / 2 + f * (crown.width - rim.width) / 2, ry = rim.height / 2 + f * (crown.height - rim.height) / 2
        return (CGPoint(x: crown.midX + rx * cos(t), y: crown.midY + ry * sin(t)), atan2(ry * cos(t), -rx * sin(t)), sesame)
    }
    return (outer, outer.offsetBy(dx: 0, dy: -drop), crown, rim, hole, hole.offsetBy(dx: 0, dy: -drop), seeds)
}

/// A flat everything bagel seen from above (Nick's pick, Oct 7, 2026; restyled Oct 9 to match the Chicago and Wisconsin icons).
/// Pure ellipses and flat opaque fills, CG y-up, drawn inside the s x s square at the origin. It never paints the ground:
/// the hole is left unpainted, so it shows whatever is behind it (flag blue on the icon and on og.png).
/// One material in three tones, light from above:
///   top   #D99A55   the risen crown of the dough, the one lighter up-facing plane (Wisconsin's top face)
///   crust #C9853F   the slopes: the outer side of the ring, and a rim rolling down into the hole
///   under #9A5A22   the underside: a crescent below the ring and the far wall inside the hole (Wisconsin's seam)
/// Seeds, 8 marks of 2 kinds: 4 sesame ovals #F6EAD0 (64 x 34 at 1024) and 4 poppy dots #1E1B1A (44 at 1024).
func bagel(_ c: CGContext, _ s: CGFloat) {
    let k = s / 1024
    let L = bagelLayout(s)
    /// Fills `r` minus the hole (even-odd), so nothing is ever painted where the hole is.
    func ring(_ r: CGRect, _ hex: UInt32) {
        c.setFillColor(rgb(hex)); c.addEllipse(in: r); c.addEllipse(in: L.hole); c.fillPath(using: .evenOdd)
    }
    ring(L.under, 0x9A5A22)                            // underside, peeking out below
    ring(L.outer, 0xC9853F)                            // outer slope
    ring(L.crown, 0xD99A55)                            // crown
    ring(L.rim, 0xC9853F)                              // inner slope
    // far wall of the hole: the part of the top opening that the underside opening does not line up with
    c.saveGState()
    c.addEllipse(in: L.hole); c.clip()
    c.setFillColor(rgb(0x9A5A22)); c.addEllipse(in: L.hole); c.addEllipse(in: L.holeFloor); c.fillPath(using: .evenOdd)
    c.restoreGState()
    for (p, angle, sesame) in L.seeds {
        c.saveGState()
        c.translateBy(x: p.x, y: p.y)
        if sesame {
            c.rotate(by: angle)
            c.setFillColor(rgb(0xF6EAD0)); c.fillEllipse(in: CGRect(x: -32 * k, y: -17 * k, width: 64 * k, height: 34 * k))
        } else {
            c.setFillColor(rgb(0x1E1B1A)); c.fillEllipse(in: CGRect(x: -22 * k, y: -22 * k, width: 44 * k, height: 44 * k))
        }
        c.restoreGState()
    }
}


func icon(_ size: Int) -> CGImage {
    canvas(size, size) { c in c.setFillColor(blue); c.fill(CGRect(x: 0, y: 0, width: size, height: size)); bagel(c, CGFloat(size)) }
}
/// Opaque: the App Store icon may not have an alpha channel.
func opaque(_ img: CGImage) -> CGImage {
    let ctx = CGContext(data: nil, width: img.width, height: img.height, bitsPerComponent: 8, bytesPerRow: 0,
                        space: CGColorSpace(name: CGColorSpace.sRGB)!, bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.draw(img, in: CGRect(x: 0, y: 0, width: img.width, height: img.height))
    return ctx.makeImage()!
}
func text(_ c: CGContext, _ str: String, font: NSFont, color: CGColor, at p: CGPoint) {
    let attr = NSAttributedString(string: str, attributes: [.font: font, .foregroundColor: NSColor(cgColor: color)!])
    c.textPosition = p; CTLineDraw(CTLineCreateWithAttributedString(attr), c)
}
func heavy(_ size: CGFloat) -> NSFont { NSFont(name: "HelveticaNeue-CondensedBlack", size: size) ?? NSFont.systemFont(ofSize: size, weight: .black) }

let args = Array(CommandLine.arguments.dropFirst())
let ogOnly = args.first == "og"
if !ogOnly {
    let appIcon = opaque(icon(1024))
    save(appIcon, "NewYorkEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png")
    save(appIcon, "docs/brand/icon-1024.png")
    save(opaque(icon(512)), "docs/icon-512.png")
    save(opaque(icon(192)), "docs/icon-192.png")
    save(opaque(icon(180)), "docs/apple-touch-icon.png")
    save(opaque(icon(32)), "docs/favicon-32.png")
}
/// The tagline carries the directory's real counts (from the data), never "every restaurant".
func ogLine() -> String? {
    if ogOnly && args.count > 1 { return args[1] }
    let url = URL(fileURLWithPath: root + "/playbook/site-numbers.json")
    guard let data = try? Data(contentsOf: url), let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
          let line = json["og_line"] as? String else { return nil }
    return line
}
if let tagline = ogLine() {
    let og = canvas(1200, 630) { c in
        c.setFillColor(blue); c.fill(CGRect(x: 0, y: 0, width: 1200, height: 630))
        c.setFillColor(gold); c.fill(CGRect(x: 72, y: 470, width: 90, height: 12))
        text(c, "NEW YORK", font: heavy(118), color: white, at: CGPoint(x: 66, y: 330))
        text(c, "EATS", font: heavy(118), color: gold, at: CGPoint(x: 66, y: 215))
        text(c, tagline, font: NSFont.systemFont(ofSize: 30, weight: .semibold), color: white, at: CGPoint(x: 70, y: 150))
        text(c, "Free for iPhone and iPad", font: NSFont.systemFont(ofSize: 28, weight: .regular), color: gold, at: CGPoint(x: 70, y: 98))
        c.saveGState(); c.translateBy(x: 790, y: 135); bagel(c, 380); c.restoreGState()
    }
    save(opaque(og), "docs/og.png")
} else {
    print("no og_line in playbook/site-numbers.json yet: run scripts/make-site.py, then make-brand.swift og")
}
