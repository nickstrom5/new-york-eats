// Three flat app-icon concepts for Nick to pick from: an everything bagel, a black-and-white cookie, a Buffalo wing with celery.
// Flat colors on the provisional state-flag blue (no gloss: Nick asked for flat icons in Colorado and Washington).
// Usage: swift scripts/icon-concepts.swift   (run from ny-eats/) -> playbook/icon-concepts.png and playbook/icon-<name>-1024.png
import AppKit
import CoreGraphics

let root = FileManager.default.currentDirectoryPath
func rgb(_ hex: UInt32, _ a: CGFloat = 1) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 0xFF) / 255, green: CGFloat((hex >> 8) & 0xFF) / 255, blue: CGFloat(hex & 0xFF) / 255, alpha: a)
}
let blue = rgb(0x14325C), gold = rgb(0xE0A526), white = rgb(0xFFFFFF), gray = rgb(0x7C878E)

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
/// A smooth closed blob around (cx, cy): an ellipse whose radius wobbles by `noise` (deterministic).
func blob(_ cx: CGFloat, _ cy: CGFloat, _ rx: CGFloat, _ ry: CGFloat, noise: CGFloat, seed: CGFloat, n: Int = 48) -> CGPath {
    var pts: [CGPoint] = []
    for i in 0..<n {
        let t = CGFloat(i) / CGFloat(n) * 2 * .pi
        let k = 1 + noise * (0.55 * sin(3 * t + seed) + 0.3 * sin(7 * t + 2 * seed) + 0.15 * sin(13 * t + 3 * seed))
        pts.append(CGPoint(x: cx + rx * k * cos(t), y: cy + ry * k * sin(t)))
    }
    let p = CGMutablePath()
    let mid = { (a: CGPoint, b: CGPoint) in CGPoint(x: (a.x + b.x) / 2, y: (a.y + b.y) / 2) }
    p.move(to: mid(pts[n - 1], pts[0]))
    for i in 0..<n { p.addQuadCurve(to: mid(pts[i], pts[(i + 1) % n]), control: pts[i]) }
    p.closeSubpath()
    return p
}
/// Deterministic pseudo-random numbers so every render shows the same seeds.
struct LCG { var s: UInt64; mutating func next() -> CGFloat { s = s &* 6364136223846793005 &+ 1442695040888963407; return CGFloat((s >> 33) % 10_000) / 10_000 } }

// ---- concept A: an everything bagel from above (the hole shows the blue ground)
func bagel(_ c: CGContext, _ s: CGFloat) {
    let cx = s * 0.5, cy = s * 0.5
    let outer = blob(cx, cy, s * 0.39, s * 0.37, noise: 0.025, seed: 0.7), hole = blob(cx, cy + s * 0.01, s * 0.115, s * 0.10, noise: 0.05, seed: 1.9)
    // underside shadow ring (flat, one shade darker), then the crust
    c.setFillColor(rgb(0x9A5A22)); c.addPath(blob(cx, cy - s * 0.022, s * 0.39, s * 0.37, noise: 0.025, seed: 0.7)); c.addPath(hole); c.fillPath(using: .evenOdd)
    c.saveGState()
    c.addPath(outer); c.addPath(hole); c.clip(using: .evenOdd)
    c.setFillColor(rgb(0xC9853F)); c.fill(CGRect(x: 0, y: 0, width: s, height: s))
    // a lighter top band where the bagel rises
    c.setFillColor(rgb(0xD99A55)); c.addPath(blob(cx, cy + s * 0.02, s * 0.31, s * 0.28, noise: 0.03, seed: 2.6)); c.fillPath()
    // seeds: sesame (cream ovals), poppy (near-black dots), onion and garlic flakes (pale), salt (white squares)
    var g = LCG(s: 42)
    for _ in 0..<150 {
        let a = g.next() * 2 * .pi, rr = 0.16 + g.next() * 0.21, x = cx + cos(a) * s * rr, y = cy + sin(a) * s * rr * 0.95, kind = g.next()
        c.saveGState(); c.translateBy(x: x, y: y); c.rotate(by: g.next() * .pi)
        if kind < 0.42 { c.setFillColor(rgb(0xF6EAD0)); c.fillEllipse(in: CGRect(x: -s * 0.014, y: -s * 0.007, width: s * 0.028, height: s * 0.014)) }
        else if kind < 0.8 { c.setFillColor(rgb(0x1E1B1A)); c.fillEllipse(in: CGRect(x: -s * 0.0065, y: -s * 0.0065, width: s * 0.013, height: s * 0.013)) }
        else if kind < 0.93 { c.setFillColor(rgb(0xE8C98E)); c.fill(CGRect(x: -s * 0.012, y: -s * 0.005, width: s * 0.024, height: s * 0.01)) }
        else { c.setFillColor(white); c.fill(CGRect(x: -s * 0.006, y: -s * 0.006, width: s * 0.012, height: s * 0.012)) }
        c.restoreGState()
    }
    c.restoreGState()
}

// ---- concept B: a black-and-white cookie, a little tilted
func cookie(_ c: CGContext, _ s: CGFloat) {
    let cx = s * 0.5, cy = s * 0.5, r = s * 0.37
    c.saveGState(); c.translateBy(x: cx, y: cy); c.rotate(by: 0.42); c.translateBy(x: -cx, y: -cy)
    c.setFillColor(rgb(0xC98A43)); c.fillEllipse(in: CGRect(x: cx - r, y: cy - r - s * 0.02, width: r * 2, height: r * 2))   // cake edge
    c.setFillColor(rgb(0xE7B470)); c.fillEllipse(in: CGRect(x: cx - r, y: cy - r, width: r * 2, height: r * 2))
    let icing = r * 0.93
    c.saveGState(); c.addEllipse(in: CGRect(x: cx - icing, y: cy - icing, width: icing * 2, height: icing * 2)); c.clip()
    c.setFillColor(rgb(0xFBF6EC)); c.fill(CGRect(x: cx - icing, y: cy - icing, width: icing, height: icing * 2))           // vanilla half
    c.setFillColor(rgb(0x2B1A12)); c.fill(CGRect(x: cx, y: cy - icing, width: icing, height: icing * 2))                    // chocolate half
    c.restoreGState()
    c.restoreGState()
}

// ---- concept C: a Buffalo wing (drumette) leaning on a celery stick
func wing(_ c: CGContext, _ s: CGFloat) {
    // celery stick: a long rounded bar with ribs and a leafy top
    c.saveGState(); c.translateBy(x: s * 0.5, y: s * 0.5); c.rotate(by: -0.62); c.translateBy(x: -s * 0.5, y: -s * 0.5)
    let stalk = CGRect(x: s * 0.13, y: s * 0.58, width: s * 0.70, height: s * 0.13)
    c.setFillColor(rgb(0x7DB84A)); c.addPath(CGPath(roundedRect: stalk, cornerWidth: s * 0.06, cornerHeight: s * 0.06, transform: nil)); c.fillPath()
    c.setFillColor(rgb(0x9FD06A)); c.addPath(CGPath(roundedRect: stalk.insetBy(dx: s * 0.02, dy: s * 0.035).offsetBy(dx: 0, dy: s * 0.02), cornerWidth: s * 0.03, cornerHeight: s * 0.03, transform: nil)); c.fillPath()
    c.setFillColor(rgb(0x5E9A35))
    for (x, y, r) in [(0.84, 0.66, 0.06), (0.89, 0.60, 0.05), (0.88, 0.72, 0.045)] as [(CGFloat, CGFloat, CGFloat)] { c.addPath(blob(s * x, s * y, s * r, s * r, noise: 0.18, seed: x * 7)); c.fillPath() }
    c.restoreGState()
    // the wing: a drumette, meaty and round at one end, narrowing to a bone with a knob at the other
    c.saveGState(); c.translateBy(x: s * 0.5, y: s * 0.5); c.rotate(by: 0.62); c.translateBy(x: -s * 0.5, y: -s * 0.5)
    func drum(_ dx: CGFloat, _ dy: CGFloat) -> CGPath {
        let p = CGMutablePath()
        p.move(to: CGPoint(x: s * (0.62 + dx), y: s * (0.50 + dy)))
        p.addCurve(to: CGPoint(x: s * (0.16 + dx), y: s * (0.44 + dy)), control1: CGPoint(x: s * (0.52 + dx), y: s * (0.68 + dy)), control2: CGPoint(x: s * (0.18 + dx), y: s * (0.66 + dy)))
        p.addCurve(to: CGPoint(x: s * (0.62 + dx), y: s * (0.40 + dy)), control1: CGPoint(x: s * (0.14 + dx), y: s * (0.24 + dy)), control2: CGPoint(x: s * (0.50 + dx), y: s * (0.26 + dy)))
        p.closeSubpath(); return p
    }
    c.setFillColor(rgb(0xF2E6D2))                                                                                      // the bone and its knob
    c.fill(CGRect(x: s * 0.58, y: s * 0.425, width: s * 0.17, height: s * 0.05))
    c.fillEllipse(in: CGRect(x: s * 0.72, y: s * 0.395, width: s * 0.08, height: s * 0.065)); c.fillEllipse(in: CGRect(x: s * 0.72, y: s * 0.44, width: s * 0.08, height: s * 0.065))
    c.setFillColor(rgb(0xA8300F)); c.addPath(drum(0, -0.018)); c.fillPath()                                           // sauce shadow
    c.setFillColor(rgb(0xD9461A)); c.addPath(drum(0, 0)); c.fillPath()                                                 // hot sauce glaze
    c.setFillColor(rgb(0xEE6A2E))
    for (x, y, rx, ry) in [(0.30, 0.52, 0.075, 0.035), (0.44, 0.53, 0.05, 0.022), (0.27, 0.42, 0.04, 0.02)] as [(CGFloat, CGFloat, CGFloat, CGFloat)] {
        c.addPath(blob(s * x, s * y, s * rx, s * ry, noise: 0.1, seed: x * 5)); c.fillPath()
    }
    c.restoreGState()
}

let concepts: [(String, String, (CGContext, CGFloat) -> Void)] = [("bagel", "A · Everything bagel", bagel), ("cookie", "B · Black-and-white cookie", cookie), ("wing", "C · Buffalo wing & celery", wing)]
func icon(_ size: Int, _ f: (CGContext, CGFloat) -> Void) -> CGImage {
    canvas(size, size) { c in c.setFillColor(blue); c.fill(CGRect(x: 0, y: 0, width: size, height: size)); f(c, CGFloat(size)) }
}
for (n, _, f) in concepts { save(icon(1024, f), "playbook/icon-\(n)-1024.png") }

func text(_ c: CGContext, _ str: String, size: CGFloat, color: CGColor, at p: CGPoint, weight: NSFont.Weight = .semibold) {
    let attr = NSAttributedString(string: str, attributes: [.font: NSFont.systemFont(ofSize: size, weight: weight), .foregroundColor: NSColor(cgColor: color)!])
    c.textPosition = p; CTLineDraw(CTLineCreateWithAttributedString(attr), c)
}
// contact sheet: each concept at 420 (≈512 on a phone), 180 and 60 px with the iOS corner mask, on light and dark grounds
let W = 1500, H = 1020
let sheet = canvas(W, H) { c in
    c.setFillColor(rgb(0xF2F4F8)); c.fill(CGRect(x: 0, y: 0, width: W, height: H))
    c.setFillColor(rgb(0x1C1C1E)); c.fill(CGRect(x: 0, y: 0, width: W, height: 150))
    for (i, (_, label, f)) in concepts.enumerated() {
        let x0 = CGFloat(40 + i * 490)
        text(c, label, size: 30, color: blue, at: CGPoint(x: x0, y: CGFloat(H) - 60))
        for (sz, y) in [(420, 420), (180, 190)] as [(Int, Int)] {
            let img = icon(sz, f), r = CGRect(x: x0, y: CGFloat(y), width: CGFloat(sz), height: CGFloat(sz))
            c.saveGState(); c.addPath(CGPath(roundedRect: r, cornerWidth: CGFloat(sz) * 0.225, cornerHeight: CGFloat(sz) * 0.225, transform: nil)); c.clip(); c.draw(img, in: r); c.restoreGState()
        }
        text(c, "420 · 180 · 60 px", size: 18, color: gray, at: CGPoint(x: x0 + 200, y: 260), weight: .regular)
        let light = icon(60, f), lr = CGRect(x: x0 + 200, y: 190, width: 60, height: 60)
        c.saveGState(); c.addPath(CGPath(roundedRect: lr, cornerWidth: 13.5, cornerHeight: 13.5, transform: nil)); c.clip(); c.draw(light, in: lr); c.restoreGState()
        let img = icon(60, f), r = CGRect(x: x0 + 40, y: 45, width: 60, height: 60)
        c.saveGState(); c.addPath(CGPath(roundedRect: r, cornerWidth: 13.5, cornerHeight: 13.5, transform: nil)); c.clip(); c.draw(img, in: r); c.restoreGState()
        text(c, "NY Eats", size: 15, color: white, at: CGPoint(x: x0 + 42, y: 22), weight: .regular)
    }
}
save(sheet, "playbook/icon-concepts.png")
