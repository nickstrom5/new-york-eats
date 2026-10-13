import SwiftUI

/// New York state-flag palette (provisional until Nick picks), light only: deep blue #14325C (12.8:1 on white) for type and fills,
/// buff gold #E0A526 only ever as a fill under dark text (2.2:1 as text, failing AA). No team marks, no state seal or arms.
enum Theme {
    static let navy = Color(hex: 0x14325C)
    static let navy2 = Color(hex: 0x24497F)
    /// gold: a fill with `onAccent` (deep blue) text on it, never text itself
    static let accent = Color(hex: 0xE0A526)
    static let onAccent = Color(hex: 0x14325C)
    static let accentSoft = Color(hex: 0xF7E3B3)
    static let onAccentSoft = Color(hex: 0x5A3E00)
    /// map pins for hand-checked places: a darker gold that holds up on Apple's map tiles
    static let markerAccent = Color(hex: 0xC98F12)
    static let gray = Color(hex: 0x7C878E)
    static let ink = Color(hex: 0x0F1A2C)
    static let ink2 = Color(hex: 0x2A3A55)
    static let muted = Color(hex: 0x4C5870)
    static let surface = Color.white
    static let surface2 = Color(hex: 0xF1F4F8)
    static let surface3 = Color(hex: 0xE0E6EF)
    static let rule = Color(hex: 0xDCE2EC)
    static let rule2 = Color(hex: 0xB5C0D3)

    /// NYC letter grades as DOHMH posts them: a blue A, a green B, an orange C card. Pending/not-yet-graded in gray.
    static let gradeColors: [String: Color] = ["A": Color(hex: 0x14325C), "B": Color(hex: 0x1B6B3A), "C": Color(hex: 0xA04A00)]
}

extension Color {
    init(hex: UInt32) {
        self.init(red: Double((hex >> 16) & 0xFF) / 255, green: Double((hex >> 8) & 0xFF) / 255, blue: Double(hex & 0xFF) / 255)
    }
}

/// A small uppercase label: "SLICES", "SEASONAL".
struct Chip: View {
    enum Style { case accent, navy, plain, dashed }
    let text: String
    var style: Style = .plain

    var body: some View {
        Text(text.uppercased())
            .font(.caption2.weight(.bold))
            .tracking(0.4)
            .padding(.horizontal, 7).padding(.vertical, 3)
            .foregroundStyle(style == .navy ? Color.white : style == .accent ? Theme.onAccentSoft : style == .dashed ? Theme.muted : Theme.navy)
            .background {
                RoundedRectangle(cornerRadius: 5).fill(style == .accent ? Theme.accentSoft : style == .navy ? Theme.navy : style == .dashed ? .clear : Theme.surface2)
            }
            .overlay {
                if style == .dashed { RoundedRectangle(cornerRadius: 5).strokeBorder(Theme.rule2, style: StrokeStyle(lineWidth: 1, dash: [3, 2])) }
            }
            .accessibilityLabel(text)
    }
}

/// An official NYC letter grade (DOHMH), drawn like the card in the window: the letter on white inside a colored frame.
struct GradeBadge: View {
    let grade: String
    var size: CGFloat = 22

    var body: some View {
        let color = Theme.gradeColors[grade] ?? Theme.muted
        Text(["N", "Z", "P"].contains(grade) ? "—" : grade)
            .displayFont(size * 0.66)
            .foregroundStyle(color)
            .frame(width: size, height: size)
            .background(RoundedRectangle(cornerRadius: size * 0.22).fill(Color.white))
            .overlay(RoundedRectangle(cornerRadius: size * 0.22).strokeBorder(color, lineWidth: max(2, size * 0.07)))
            .accessibilityLabel(["A": "NYC grade A", "B": "NYC grade B", "C": "NYC grade C"][grade] ?? "NYC grade pending")
    }
}

/// An NYC grade as a chip: the little grade card and the month it was graded ("A  Feb 2026").
struct GradeChip: View {
    let grade: String
    let date: String?

    var body: some View {
        HStack(spacing: 5) {
            GradeBadge(grade: grade, size: 17)
            if let date { Text(date.uppercased()).font(.caption2.weight(.bold)).tracking(0.4).foregroundStyle(Theme.navy) }
        }
        .padding(.leading, 2).padding(.trailing, date == nil ? 2 : 7).padding(.vertical, 2)
        .background(RoundedRectangle(cornerRadius: 6).fill(Theme.surface2))
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("NYC grade \(grade)" + (date.map { ", graded \($0)" } ?? ""))
    }
}

/// The state's outline with Long Island picked out in gold: the one New York element in the header (no skyline, no subway bullets).
struct StateBand: View {
    /// upstate's color: flag blue on white, white on the blue masthead
    var fill: Color = Theme.navy

    var body: some View {
        ZStack(alignment: .leading) {
            StateShape().fill(fill)
            StateShape(longIsland: true).fill(Theme.accent)
        }
        .aspectRatio(StateOutline.aspect, contentMode: .fit)
        .accessibilityHidden(true)
    }
}

/// Condensed, heavy display type for titles and big numbers (the system font's compressed width). It scales with the
/// reader's text size, capped at 1.6× so a big number can't swallow its row.
struct DisplayFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .black
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight).width(.compressed))
    }
}

extension View {
    func displayFont(_ size: CGFloat, weight: Font.Weight = .black) -> some View {
        modifier(DisplayFont(size: size, weight: weight))
    }
}
