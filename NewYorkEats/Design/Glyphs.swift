import SwiftUI

/// Flat, one-color food glyphs for the New York classics (the app icon's everything bagel is the model): a slice with its crust and
/// pepperoni, a seeded bagel, a Buffalo wing, a hot dog in its bun, a black-and-white half-moon cookie, a pleated dumpling.
/// Drawn in a unit square and filled even-odd, so holes (pepperoni, seeds, the bun's slot) read at any size.
enum FoodGlyph {
    case slice, bagel, wing, hotDog, halfMoon, dumpling

    static func of(_ guide: Guide) -> FoodGlyph? {
        switch guide {
        case .slices: .slice
        case .bagels: .bagel
        case .wings: .wing
        case .hots: .hotDog
        case .upstate: .halfMoon
        case .dimSum: .dumpling
        default: nil
        }
    }

    func path(in r: CGRect) -> Path {
        let s = min(r.width, r.height)
        let o = CGPoint(x: r.midX - s / 2, y: r.midY - s / 2)
        func p(_ x: CGFloat, _ y: CGFloat) -> CGPoint { CGPoint(x: o.x + x * s, y: o.y + y * s) }
        func circle(_ x: CGFloat, _ y: CGFloat, _ rad: CGFloat) -> CGRect { CGRect(x: o.x + (x - rad) * s, y: o.y + (y - rad) * s, width: 2 * rad * s, height: 2 * rad * s) }
        var path = Path()
        switch self {
        case .slice:
            path.addRoundedRect(in: CGRect(x: o.x + 0.10 * s, y: o.y + 0.10 * s, width: 0.80 * s, height: 0.17 * s), cornerSize: CGSize(width: 0.085 * s, height: 0.085 * s))
            path.move(to: p(0.15, 0.31)); path.addLine(to: p(0.85, 0.31)); path.addLine(to: p(0.5, 0.93)); path.closeSubpath()
            for (x, y, rad) in [(0.39, 0.43, 0.065), (0.61, 0.47, 0.06), (0.49, 0.65, 0.055)] { path.addEllipse(in: circle(x, y, rad)) }
        case .bagel:
            path.addEllipse(in: circle(0.5, 0.5, 0.44))
            path.addEllipse(in: circle(0.5, 0.5, 0.14))
            // an everything bagel's seeds: round dots of a few sizes scattered over the ring
            for (a, rr, rad) in [(0.2, 0.30, 0.030), (0.9, 0.25, 0.024), (1.5, 0.33, 0.028), (2.2, 0.27, 0.022), (2.8, 0.32, 0.030),
                                 (3.5, 0.26, 0.024), (4.1, 0.33, 0.027), (4.8, 0.28, 0.022), (5.5, 0.31, 0.029), (6.0, 0.24, 0.020)] as [(Double, CGFloat, CGFloat)] {
                path.addEllipse(in: circle(0.5 + rr * CGFloat(cos(a)), 0.5 + rr * CGFloat(sin(a)), rad))
            }
        case .wing:   // a drumette: the meaty end, the bone, two knuckles, as one shape
            var meat = Path(); meat.addEllipse(in: circle(0.60, 0.40, 0.29))
            let bone = Path(roundedRect: CGRect(x: -0.065 * s, y: -0.25 * s, width: 0.13 * s, height: 0.50 * s), cornerRadius: 0.065 * s)
                .applying(CGAffineTransform(rotationAngle: .pi / 4)).applying(CGAffineTransform(translationX: o.x + 0.34 * s, y: o.y + 0.66 * s))
            var knuckles = Path(); knuckles.addEllipse(in: circle(0.12, 0.79, 0.08)); knuckles.addEllipse(in: circle(0.21, 0.88, 0.08))
            path = meat.union(bone).union(knuckles, eoFill: false)
        case .hotDog:   // side on: the bun as a boat, the dog lying in it and running past both ends
            let t = CGAffineTransform(translationX: o.x + 0.5 * s, y: o.y + 0.54 * s).rotated(by: -.pi / 7)
            func capsule(_ w: CGFloat, _ h: CGFloat, _ dy: CGFloat = 0) -> Path {
                Path(roundedRect: CGRect(x: -w / 2 * s, y: (dy - h / 2) * s, width: w * s, height: h * s), cornerRadius: h / 2 * s).applying(t)
            }
            path = capsule(0.84, 0.56).subtracting(capsule(1.1, 0.40, -0.16)).union(capsule(1.0, 0.22, -0.095))
        case .halfMoon:   // Utica and Binghamton's half-moon cookie: one half fudge, one half vanilla
            path.addEllipse(in: circle(0.5, 0.5, 0.44))
            path.addEllipse(in: circle(0.5, 0.5, 0.36))
            path.move(to: p(0.5, 0.14))
            path.addArc(center: p(0.5, 0.5), radius: 0.36 * s, startAngle: .degrees(-90), endAngle: .degrees(90), clockwise: true)
            path.closeSubpath()
        case .dumpling:   // dim sum's bamboo steamer: a domed lid with its knob, the basket with two bands of weave
            path.addRoundedRect(in: CGRect(x: o.x + 0.44 * s, y: o.y + 0.12 * s, width: 0.12 * s, height: 0.10 * s), cornerSize: CGSize(width: 0.03 * s, height: 0.03 * s))
            path.move(to: p(0.10, 0.45))
            path.addCurve(to: p(0.90, 0.45), control1: p(0.14, 0.16), control2: p(0.86, 0.16))
            path.closeSubpath()
            path.addRoundedRect(in: CGRect(x: o.x + 0.08 * s, y: o.y + 0.50 * s, width: 0.84 * s, height: 0.36 * s), cornerSize: CGSize(width: 0.07 * s, height: 0.07 * s))
            for y in [0.60, 0.72] as [CGFloat] {
                path.addRoundedRect(in: CGRect(x: o.x + 0.16 * s, y: o.y + y * s, width: 0.68 * s, height: 0.045 * s), cornerSize: CGSize(width: 0.02 * s, height: 0.02 * s))
            }
        }
        return path
    }
}

struct FoodGlyphShape: Shape {
    let glyph: FoodGlyph
    func path(in rect: CGRect) -> Path { glyph.path(in: rect) }
}

/// A guide's mark: its food glyph for the classics, its SF Symbol for the rest.
struct GuideGlyph: View {
    let guide: Guide
    var size: CGFloat = 22
    var color: Color = Theme.navy

    var body: some View {
        Group {
            if let g = FoodGlyph.of(guide) {
                FoodGlyphShape(glyph: g).fill(color, style: FillStyle(eoFill: true)).frame(width: size, height: size)
            } else {
                Image(systemName: guide.systemImage).font(.system(size: size * 0.8, weight: .semibold)).foregroundStyle(color)
                    .frame(width: size, height: size)
            }
        }
        .accessibilityHidden(true)
    }
}

#Preview {
    HStack(spacing: 18) {
        ForEach([Guide.slices, .bagels, .wings, .hots, .upstate, .dimSum]) { GuideGlyph(guide: $0, size: 44) }
    }
    .padding()
}
