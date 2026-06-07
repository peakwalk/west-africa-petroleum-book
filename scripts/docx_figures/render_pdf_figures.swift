import AppKit
import Foundation
import ImageIO
import PDFKit

struct Config {
    var pdfPath: String = ""
    var outputDir: String = ""
    var figures: [Int] = []
    var scale: CGFloat = 6.0
    var sideMargin: CGFloat = 40.0
    var topMargin: CGFloat = 40.0
    var captionGap: CGFloat = 10.0
    var interFigureGap: CGFloat = 12.0
    var cropPadding: CGFloat = 8.0
}

struct CaptionBounds {
    let x: CGFloat
    let y: CGFloat
    let width: CGFloat
    let height: CGFloat
    let pageWidth: CGFloat
    let pageHeight: CGFloat

    var top: CGFloat { y + height }
}

struct CaptionPlacement {
    let figureNumber: Int
    let pageNumber: Int
    let captionBounds: CaptionBounds
}

struct SearchWindow {
    let figureNumber: Int
    let pageNumber: Int
    let left: CGFloat
    let right: CGFloat
    let bottom: CGFloat
    let top: CGFloat
}

enum RenderError: Error, CustomStringConvertible {
    case invalidArguments(String)
    case failedToOpenPdf(String)
    case failedToFindCaption(Int)
    case failedToRenderPage(Int)
    case failedToCropFigure(Int)
    case failedToEncodePng(Int)

    var description: String {
        switch self {
        case .invalidArguments(let message):
            return message
        case .failedToOpenPdf(let path):
            return "Failed to open PDF at \(path)"
        case .failedToFindCaption(let figureNumber):
            return "Failed to locate a PDF caption for Figure \(figureNumber)"
        case .failedToRenderPage(let pageNumber):
            return "Failed to render PDF page \(pageNumber)"
        case .failedToCropFigure(let figureNumber):
            return "Failed to detect a non-white figure region for Figure \(figureNumber)"
        case .failedToEncodePng(let figureNumber):
            return "Failed to encode PNG output for Figure \(figureNumber)"
        }
    }
}

func parseArguments() throws -> Config {
    var config = Config()
    var index = 1
    let args = CommandLine.arguments
    while index < args.count {
        let key = args[index]
        switch key {
        case "--pdf":
            index += 1
            guard index < args.count else { throw RenderError.invalidArguments("Missing value for --pdf") }
            config.pdfPath = args[index]
        case "--output-dir":
            index += 1
            guard index < args.count else { throw RenderError.invalidArguments("Missing value for --output-dir") }
            config.outputDir = args[index]
        case "--figures":
            index += 1
            guard index < args.count else { throw RenderError.invalidArguments("Missing value for --figures") }
            config.figures = args[index]
                .split(separator: ",")
                .compactMap { Int($0.trimmingCharacters(in: .whitespaces)) }
        case "--scale":
            index += 1
            guard index < args.count, let value = Double(args[index]) else {
                throw RenderError.invalidArguments("Missing numeric value for --scale")
            }
            config.scale = CGFloat(value)
        case "--side-margin":
            index += 1
            guard index < args.count, let value = Double(args[index]) else {
                throw RenderError.invalidArguments("Missing numeric value for --side-margin")
            }
            config.sideMargin = CGFloat(value)
        case "--top-margin":
            index += 1
            guard index < args.count, let value = Double(args[index]) else {
                throw RenderError.invalidArguments("Missing numeric value for --top-margin")
            }
            config.topMargin = CGFloat(value)
        case "--caption-gap":
            index += 1
            guard index < args.count, let value = Double(args[index]) else {
                throw RenderError.invalidArguments("Missing numeric value for --caption-gap")
            }
            config.captionGap = CGFloat(value)
        case "--inter-figure-gap":
            index += 1
            guard index < args.count, let value = Double(args[index]) else {
                throw RenderError.invalidArguments("Missing numeric value for --inter-figure-gap")
            }
            config.interFigureGap = CGFloat(value)
        case "--crop-padding":
            index += 1
            guard index < args.count, let value = Double(args[index]) else {
                throw RenderError.invalidArguments("Missing numeric value for --crop-padding")
            }
            config.cropPadding = CGFloat(value)
        default:
            throw RenderError.invalidArguments("Unknown argument \(key)")
        }
        index += 1
    }

    if config.pdfPath.isEmpty || config.outputDir.isEmpty || config.figures.isEmpty {
        throw RenderError.invalidArguments("Expected --pdf, --output-dir, and --figures")
    }
    return config
}

func bestPlacement(document: PDFDocument, figureNumber: Int) -> CaptionPlacement? {
    let needle = "Figure \(figureNumber):"
    let selections = document.findString(needle, withOptions: .caseInsensitive)
    let placements = selections.compactMap { selection -> CaptionPlacement? in
        guard let page = selection.pages.first else { return nil }
        let bounds = selection.bounds(for: page)
        let pageBounds = page.bounds(for: .mediaBox)
        return CaptionPlacement(
            figureNumber: figureNumber,
            pageNumber: document.index(for: page) + 1,
            captionBounds: CaptionBounds(
                x: bounds.origin.x,
                y: bounds.origin.y,
                width: bounds.width,
                height: bounds.height,
                pageWidth: pageBounds.width,
                pageHeight: pageBounds.height
            )
        )
    }
    return placements.max { lhs, rhs in
        if lhs.pageNumber == rhs.pageNumber {
            return lhs.captionBounds.y < rhs.captionBounds.y
        }
        return lhs.pageNumber < rhs.pageNumber
    }
}

func buildSearchWindows(placements: [CaptionPlacement], config: Config) -> [SearchWindow] {
    let grouped = Dictionary(grouping: placements, by: { $0.pageNumber })
    var windows: [SearchWindow] = []
    for (pageNumber, pagePlacements) in grouped {
        let sortedPlacements = pagePlacements.sorted { $0.captionBounds.y < $1.captionBounds.y }
        for (index, placement) in sortedPlacements.enumerated() {
            let nextHigher = index + 1 < sortedPlacements.count ? sortedPlacements[index + 1] : nil
            let bounds = placement.captionBounds
            var top = nextHigher.map { $0.captionBounds.y - config.interFigureGap }
                ?? (bounds.pageHeight - config.topMargin)
            let bottom = bounds.top + config.captionGap
            if top <= bottom {
                top = min(bounds.pageHeight - config.topMargin, bottom + 24.0)
            }
            windows.append(
                SearchWindow(
                    figureNumber: placement.figureNumber,
                    pageNumber: pageNumber,
                    left: config.sideMargin,
                    right: bounds.pageWidth - config.sideMargin,
                    bottom: bottom,
                    top: top
                )
            )
        }
    }
    return windows.sorted { $0.figureNumber < $1.figureNumber }
}

func renderPage(_ page: PDFPage, scale: CGFloat) -> NSBitmapImageRep? {
    let bounds = page.bounds(for: .mediaBox)
    let pixelWidth = Int((bounds.width * scale).rounded())
    let pixelHeight = Int((bounds.height * scale).rounded())
    let colorSpace = CGColorSpaceCreateDeviceRGB()
    let bitmapInfo = CGImageAlphaInfo.premultipliedLast.rawValue
    guard let context = CGContext(
        data: nil,
        width: pixelWidth,
        height: pixelHeight,
        bitsPerComponent: 8,
        bytesPerRow: 0,
        space: colorSpace,
        bitmapInfo: bitmapInfo
    ) else {
        return nil
    }
    context.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    context.fill(CGRect(x: 0, y: 0, width: CGFloat(pixelWidth), height: CGFloat(pixelHeight)))
    context.scaleBy(x: scale, y: scale)
    page.draw(with: .mediaBox, to: context)
    guard let image = context.makeImage() else {
        return nil
    }
    return NSBitmapImageRep(cgImage: image)
}

func findContentBounds(
    bitmap: NSBitmapImageRep,
    pageHeight: CGFloat,
    scale: CGFloat,
    searchWindow: SearchWindow
) -> CGRect? {
    guard let data = bitmap.bitmapData else { return nil }
    let bytesPerRow = bitmap.bytesPerRow
    let minX = max(0, Int(floor(searchWindow.left * scale)))
    let maxX = min(bitmap.pixelsWide - 1, Int(ceil(searchWindow.right * scale)))
    let minYPixel = max(0, Int(floor((pageHeight - searchWindow.top) * scale)))
    let maxYPixel = min(bitmap.pixelsHigh - 1, Int(ceil((pageHeight - searchWindow.bottom) * scale)))
    let rowThreshold = 8
    let maxGapRows = max(8, Int((scale * 2).rounded()))
    var rowCounts: [(pixelY: Int, count: Int)] = []
    for py in minYPixel...maxYPixel {
        let row = data + py * bytesPerRow
        var count = 0
        for px in minX...maxX {
            let offset = px * 4
            let r = row[offset]
            let g = row[offset + 1]
            let b = row[offset + 2]
            let a = row[offset + 3]
            if a > 8 && (r < 248 || g < 248 || b < 248) {
                count += 1
            }
        }
        rowCounts.append((pixelY: py, count: count))
    }

    struct Band {
        var start: Int
        var end: Int
        var score: Int
    }

    var bands: [Band] = []
    for row in rowCounts where row.count >= rowThreshold {
        if var last = bands.last, row.pixelY - last.end <= maxGapRows {
            last.end = row.pixelY
            last.score += row.count
            bands[bands.count - 1] = last
        } else {
            bands.append(Band(start: row.pixelY, end: row.pixelY, score: row.count))
        }
    }

    guard let band = bands.max(by: { lhs, rhs in
        if lhs.score == rhs.score {
            return (lhs.end - lhs.start) < (rhs.end - rhs.start)
        }
        return lhs.score < rhs.score
    }) else {
        return nil
    }

    var found = false
    var left = maxX
    var right = minX
    var top = band.end
    var bottom = band.start
    for py in band.start...band.end {
        let row = data + py * bytesPerRow
        for px in minX...maxX {
            let offset = px * 4
            let r = row[offset]
            let g = row[offset + 1]
            let b = row[offset + 2]
            let a = row[offset + 3]
            if a > 8 && (r < 248 || g < 248 || b < 248) {
                found = true
                if px < left { left = px }
                if px > right { right = px }
                if py < top { top = py }
                if py > bottom { bottom = py }
            }
        }
    }

    if !found {
        return nil
    }

    return CGRect(
        x: CGFloat(left) / scale,
        y: pageHeight - CGFloat(bottom + 1) / scale,
        width: CGFloat(right - left + 1) / scale,
        height: CGFloat(bottom - top + 1) / scale
    )
}

func expandBounds(_ rect: CGRect, pageBounds: CGRect, padding: CGFloat) -> CGRect {
    let expanded = rect.insetBy(dx: -padding, dy: -padding)
    return expanded.intersection(pageBounds)
}

func cropImage(
    bitmap: NSBitmapImageRep,
    pageRect: CGRect,
    pageHeight: CGFloat,
    scale: CGFloat
) -> CGImage? {
    guard let cgImage = bitmap.cgImage else {
        return nil
    }
    let cropRect = CGRect(
        x: floor(pageRect.minX * scale),
        y: floor((pageHeight - pageRect.maxY) * scale),
        width: ceil(pageRect.width * scale),
        height: ceil(pageRect.height * scale)
    ).integral
    return cgImage.cropping(to: cropRect)
}

func writeImage(_ image: CGImage, to url: URL, typeIdentifier: CFString) -> Bool {
    guard let destination = CGImageDestinationCreateWithURL(url as CFURL, typeIdentifier, 1, nil) else {
        return false
    }
    CGImageDestinationAddImage(destination, image, nil)
    return CGImageDestinationFinalize(destination)
}

let webpSupported: Bool = {
    let identifiers = CGImageDestinationCopyTypeIdentifiers() as? [String] ?? []
    return identifiers.contains("org.webmproject.webp")
}()

do {
    let config = try parseArguments()
    guard let document = PDFDocument(url: URL(fileURLWithPath: config.pdfPath)) else {
        throw RenderError.failedToOpenPdf(config.pdfPath)
    }

    let placements = try config.figures.map { figureNumber -> CaptionPlacement in
        guard let placement = bestPlacement(document: document, figureNumber: figureNumber) else {
            throw RenderError.failedToFindCaption(figureNumber)
        }
        return placement
    }
    let windowsByFigure = Dictionary(
        uniqueKeysWithValues: buildSearchWindows(placements: placements, config: config).map { ($0.figureNumber, $0) }
    )
    let placementsByFigure = Dictionary(uniqueKeysWithValues: placements.map { ($0.figureNumber, $0) })
    let outputDir = URL(fileURLWithPath: config.outputDir, isDirectory: true)
    try FileManager.default.createDirectory(at: outputDir, withIntermediateDirectories: true)

    var renderedPages: [Int: NSBitmapImageRep] = [:]
    for figureNumber in config.figures {
        guard let placement = placementsByFigure[figureNumber], let searchWindow = windowsByFigure[figureNumber] else {
            throw RenderError.failedToFindCaption(figureNumber)
        }
        let pageIndex = placement.pageNumber - 1
        guard let page = document.page(at: pageIndex) else {
            throw RenderError.failedToRenderPage(placement.pageNumber)
        }
        let pageBounds = page.bounds(for: .mediaBox)
        let bitmap = renderedPages[placement.pageNumber] ?? {
            let rendered = renderPage(page, scale: config.scale)
            if let rendered = rendered {
                renderedPages[placement.pageNumber] = rendered
            }
            return rendered
        }()
        guard let pageBitmap = bitmap else {
            throw RenderError.failedToRenderPage(placement.pageNumber)
        }
        guard let rawBounds = findContentBounds(
            bitmap: pageBitmap,
            pageHeight: pageBounds.height,
            scale: config.scale,
            searchWindow: searchWindow
        ) else {
            throw RenderError.failedToCropFigure(figureNumber)
        }
        let cropBounds = expandBounds(rawBounds, pageBounds: pageBounds, padding: config.cropPadding)
        guard let cropImage = cropImage(
            bitmap: pageBitmap,
            pageRect: cropBounds,
            pageHeight: pageBounds.height,
            scale: config.scale
        ) else {
            throw RenderError.failedToCropFigure(figureNumber)
        }

        let pngURL = outputDir.appendingPathComponent(String(format: "figure-%03d.png", figureNumber))
        guard writeImage(cropImage, to: pngURL, typeIdentifier: "public.png" as CFString) else {
            throw RenderError.failedToEncodePng(figureNumber)
        }
        print("Rendered Figure \(figureNumber) -> \(pngURL.path)")

        if webpSupported {
            let webpURL = outputDir.appendingPathComponent(String(format: "figure-%03d.webp", figureNumber))
            if writeImage(cropImage, to: webpURL, typeIdentifier: "org.webmproject.webp" as CFString) {
                print("Rendered Figure \(figureNumber) -> \(webpURL.path)")
            }
        }
    }

    if !webpSupported {
        print("WebP output skipped: no writable WebP encoder is available on this host.")
    }
} catch {
    fputs("render_pdf_figures.swift: \(error)\n", stderr)
    exit(1)
}
