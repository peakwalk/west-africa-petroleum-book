import AppKit
import Foundation
import WebKit

struct BrowserCheckError: Error, CustomStringConvertible {
    let description: String

    init(_ description: String) {
        self.description = description
    }
}

struct Config {
    let rootDir: URL
    let baseURL: URL?
    let scope: String
    let pageConfig: PageConfig
}

struct PageConfig: Decodable {
    let skippedPages: [String]
    let preserveOutlinePages: [String: [String]]
    let smokePages: [String: [String]]
}

struct ReferenceSections: Decodable {
    let figures: Bool?
    let tables: Bool?
    let formulas: Bool?
}

struct ReaderPageMeta: Decodable {
    let referenceSections: ReferenceSections?
}

struct FigureSentinelSnapshot: Decodable {
    let label: String
    let title: String
}

struct RuntimeSnapshot: Decodable {
    let timedOut: Bool
    let readyState: String
    let readerRuntimeState: String
    let outlineStateSettled: Bool
    let referenceSectionsSettled: Bool
    let bodyClasses: [String]
    let hasRefreshMeta: Bool
    let hasReaderArticle: Bool
    let hasOutlineElement: Bool
    let outlineHidden: Bool?
    let headingCount: Int
    let figureCardCount: Int
    let tableCardCount: Int
    let formulaCardCount: Int
    let figureOutlineCount: Int
    let tableOutlineCount: Int
    let formulaOutlineCount: Int
    let figureCaptionParagraphCount: Int
    let sentinelFigureFive: FigureSentinelSnapshot?
}

final class BrowserPageLoader: NSObject, WKNavigationDelegate {
    private let webView: WKWebView
    private var pendingResult: Result<RuntimeSnapshot, Error>?
    private var lastSnapshot: RuntimeSnapshot?

    override init() {
        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = .nonPersistent()
        configuration.defaultWebpagePreferences.allowsContentJavaScript = true
        self.webView = WKWebView(frame: .zero, configuration: configuration)
        super.init()
        self.webView.navigationDelegate = self
    }

    func snapshot(for pageURL: URL, readAccessURL: URL?, timeout: TimeInterval = 15) throws -> RuntimeSnapshot {
        pendingResult = nil
        lastSnapshot = nil
        webView.stopLoading()

        let navigation: WKNavigation?
        if pageURL.isFileURL {
            guard let readAccessURL else {
                throw BrowserCheckError("Missing read access root for local browser load \(pageURL.path).")
            }
            navigation = webView.loadFileURL(pageURL, allowingReadAccessTo: readAccessURL)
        } else {
            navigation = webView.load(URLRequest(url: pageURL))
        }

        guard navigation != nil else {
            throw BrowserCheckError("Failed to start browser load for \(pageURL.absoluteString).")
        }

        let deadline = Date().addingTimeInterval(timeout)
        while pendingResult == nil && Date() < deadline {
            RunLoop.current.run(mode: .default, before: Date().addingTimeInterval(0.05))
        }

        guard let pendingResult else {
            throw BrowserCheckError("Timed out loading \(pageURL.path).")
        }

        return try pendingResult.get()
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        pollRuntimeSnapshot(remainingAttempts: 80)
    }

    private func pollRuntimeSnapshot(remainingAttempts: Int) {
        webView.evaluateJavaScript(Self.runtimeProbeScript) { [weak self] value, error in
            guard let self else { return }

            if let error {
                self.complete(.failure(BrowserCheckError("Failed to evaluate browser probe: \(error.localizedDescription)")))
                return
            }

            guard let json = value as? String else {
                self.complete(.failure(BrowserCheckError("Browser probe did not return a JSON string.")))
                return
            }

            do {
                let snapshot = try JSONDecoder().decode(RuntimeSnapshot.self, from: Data(json.utf8))
                self.lastSnapshot = snapshot

                if snapshot.readyState == "complete" &&
                    snapshot.readerRuntimeState == "ready" &&
                    snapshot.outlineStateSettled &&
                    snapshot.referenceSectionsSettled
                {
                    self.complete(.success(snapshot))
                    return
                }

                if remainingAttempts <= 1 {
                    let diagnostic = self.lastSnapshot.map {
                        " readyState=\($0.readyState) runtimeState=\($0.readerRuntimeState) bodyClasses=\($0.bodyClasses.joined(separator: ",")) headingCount=\($0.headingCount) figureCards=\($0.figureCardCount) figureOutline=\($0.figureOutlineCount)"
                    } ?? ""
                    self.complete(.failure(BrowserCheckError("Timed out waiting for runtime DOM state on \(self.webView.url?.path ?? "<unknown>").\(diagnostic)")))
                    return
                }

                DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) {
                    self.pollRuntimeSnapshot(remainingAttempts: remainingAttempts - 1)
                }
            } catch {
                self.complete(.failure(BrowserCheckError("Failed to decode browser probe JSON: \(error.localizedDescription)")))
            }
        }
    }

    func webView(
        _ webView: WKWebView,
        didFail navigation: WKNavigation!,
        withError error: Error
    ) {
        if let nsError = error as NSError?, nsError.domain == NSURLErrorDomain && nsError.code == NSURLErrorCancelled {
            return
        }

        complete(.failure(BrowserCheckError("Browser navigation failed for \(webView.url?.path ?? "<unknown>"): \(error.localizedDescription)")))
    }

    func webView(
        _ webView: WKWebView,
        didFailProvisionalNavigation navigation: WKNavigation!,
        withError error: Error
    ) {
        if let nsError = error as NSError?, nsError.domain == NSURLErrorDomain && nsError.code == NSURLErrorCancelled {
            return
        }

        complete(.failure(BrowserCheckError("Browser provisional navigation failed for \(webView.url?.path ?? "<unknown>"): \(error.localizedDescription)")))
    }

    private func complete(_ result: Result<RuntimeSnapshot, Error>) {
        guard pendingResult == nil else {
            return
        }

        pendingResult = result
    }

    private static let runtimeProbeScript = #"""
    (function () {
      function normalizeText(value) {
        return String(value || "").replace(/\s+/g, " ").trim();
      }

      function isNarrativeFigureReference(text) {
        return /^Figures?\s+\d+(?:(?:\s*,\s*|\s+and\s+|\s+to\s+|\s*-\s*)(?:Figures?\s+)?\d+)*\s+(?:show|shows|illustrate|illustrates|present|presents|depict|depicts|contain|contains)\b/i.test(
          normalizeText(text)
        );
      }

      function isFigureCaptionParagraph(paragraph) {
        const text = normalizeText(paragraph.textContent || "");
        return /^Figure\s+0*(\d+)(?:\s*:\s*|\s+)/i.test(text) && !isNarrativeFigureReference(text);
      }

      function collectSnapshot(timedOut) {
        const outline = document.querySelector("#mdbook-outline-scroll");
        const figureFive = document.querySelector("#figure-5.figure-card");
        const figuresSection = document.querySelector(".book-outline-figures");
        const tablesSection = document.querySelector(".book-outline-tables");
        const formulasSection = document.querySelector(".book-outline-formulas");
        const readerRuntimeState =
          String(window.__readerRuntimeState || document.documentElement.dataset.readerRuntimeState || "").trim();
        const hasHeadingOutline = document.querySelectorAll(".book-outline-body .header-in-summary[data-target-id]").length > 0;
        const figureCardCount = document.querySelectorAll(".reader-article .figure-card").length;
        const tableCardCount = document.querySelectorAll(".reader-article .table-anchor-target").length;
        const formulaCardCount = document.querySelectorAll('.reader-article .formula-anchor-target[data-formula-nav="true"]').length;
        const figureOutlineCount = document.querySelectorAll(".book-outline-figures:not([hidden]) .book-outline-link--reference").length;
        const tableOutlineCount = document.querySelectorAll(".book-outline-tables:not([hidden]) .book-outline-link--reference").length;
        const formulaOutlineCount = document.querySelectorAll(".book-outline-formulas:not([hidden]) .book-outline-link--reference").length;
        const hasVisibleReferenceOutline =
          figureOutlineCount > 0 ||
          tableOutlineCount > 0 ||
          formulaOutlineCount > 0;
        const bodyClasses = Array.from(document.body ? document.body.classList : []);
        const figuresSectionHidden = !figuresSection || Boolean(figuresSection.hidden);
        const tablesSectionHidden = !tablesSection || Boolean(tablesSection.hidden);
        const formulasSectionHidden = !formulasSection || Boolean(formulasSection.hidden);
        const outlineStateSettled =
          bodyClasses.includes("book-outline-empty") ||
          bodyClasses.includes("book-outline-ready") ||
          bodyClasses.includes("book-page-cover") ||
          bodyClasses.includes("book-page-front-matter-outline-rail") ||
          hasHeadingOutline ||
          hasVisibleReferenceOutline;
        const referenceSectionsSettled =
          (figuresSectionHidden || figureOutlineCount === figureCardCount) &&
          (tablesSectionHidden || tableOutlineCount === tableCardCount) &&
          (formulasSectionHidden || formulaOutlineCount === formulaCardCount);

        return JSON.stringify({
          timedOut: Boolean(timedOut),
          readyState: document.readyState,
          readerRuntimeState: readerRuntimeState,
          outlineStateSettled: Boolean(outlineStateSettled),
          referenceSectionsSettled: Boolean(referenceSectionsSettled),
          bodyClasses: bodyClasses,
          hasRefreshMeta: Boolean(document.querySelector('meta[http-equiv="refresh"]')),
          hasReaderArticle: Boolean(document.querySelector(".reader-article")),
          hasOutlineElement: Boolean(outline),
          outlineHidden: outline ? Boolean(outline.hidden) : null,
          headingCount: document.querySelectorAll(".book-outline-body .header-in-summary[data-target-id]").length,
          figureCardCount: figureCardCount,
          tableCardCount: tableCardCount,
          formulaCardCount: formulaCardCount,
          figureOutlineCount: figureOutlineCount,
          tableOutlineCount: tableOutlineCount,
          formulaOutlineCount: formulaOutlineCount,
          figureCaptionParagraphCount: Array.from(document.querySelectorAll(".reader-article > p")).filter(isFigureCaptionParagraph).length,
          sentinelFigureFive: figureFive
            ? {
                label: normalizeText(figureFive.querySelector(".figure-card-label")?.textContent || ""),
                title: normalizeText(figureFive.querySelector(".figure-card-title")?.textContent || "")
              }
            : null
        });
      }

      return collectSnapshot(false);
    })();
    """#
}

func sortedChapterPages(bookRoot: URL) throws -> [String] {
    let chaptersDir = bookRoot.appendingPathComponent("chapters", isDirectory: true)
    let filenames = try FileManager.default.contentsOfDirectory(atPath: chaptersDir.path)
        .filter { $0.hasSuffix(".html") }
        .sorted()
    return filenames.map { "chapters/\($0)" }
}

func localizedFilePageURL(for fileURL: URL, locale: String) -> URL {
    var components = URLComponents(url: fileURL, resolvingAgainstBaseURL: false) ?? URLComponents()
    components.queryItems = [URLQueryItem(name: "lang", value: locale)]
    return components.url ?? fileURL
}

func parseConfig() throws -> Config {
    let rootDir = URL(fileURLWithPath: FileManager.default.currentDirectoryPath, isDirectory: true)
    var baseURL: URL? = nil
    var scope = "smoke"
    var pageConfigPath: String? = nil
    var index = 1

    while index < CommandLine.arguments.count {
        let argument = CommandLine.arguments[index]

        switch argument {
        case "--base-url":
            index += 1
            guard index < CommandLine.arguments.count else {
                throw BrowserCheckError("Missing value for --base-url.")
            }

            guard let parsedURL = URL(string: CommandLine.arguments[index]), parsedURL.scheme != nil else {
                throw BrowserCheckError("Invalid --base-url value: \(CommandLine.arguments[index]).")
            }

            baseURL = parsedURL
        case "--scope":
            index += 1
            guard index < CommandLine.arguments.count else {
                throw BrowserCheckError("Missing value for --scope.")
            }

            let requestedScope = CommandLine.arguments[index]
            guard requestedScope == "smoke" || requestedScope == "full" else {
                throw BrowserCheckError("Unsupported --scope value: \(requestedScope). Expected smoke or full.")
            }

            scope = requestedScope
        case "--page-config":
            index += 1
            guard index < CommandLine.arguments.count else {
                throw BrowserCheckError("Missing value for --page-config.")
            }

            pageConfigPath = CommandLine.arguments[index]
        default:
            throw BrowserCheckError("Unknown argument \(argument).")
        }

        index += 1
    }

    guard let pageConfigPath else {
        throw BrowserCheckError("Missing required --page-config argument.")
    }

    let pageConfigURL = URL(fileURLWithPath: pageConfigPath)

    let pageConfigData: Data
    do {
        pageConfigData = try Data(contentsOf: pageConfigURL)
    } catch {
        throw BrowserCheckError("Failed to read page config at \(pageConfigURL.path): \(error.localizedDescription)")
    }

    let pageConfig: PageConfig
    do {
        pageConfig = try JSONDecoder().decode(PageConfig.self, from: pageConfigData)
    } catch {
        throw BrowserCheckError("Failed to decode page config at \(pageConfigURL.path): \(error.localizedDescription)")
    }

    return Config(rootDir: rootDir, baseURL: baseURL, scope: scope, pageConfig: pageConfig)
}

func preservesOutlineRail(for relativePath: String, locale: String, pageConfig: PageConfig) -> Bool {
    pageConfig.preserveOutlinePages[locale]?.contains(relativePath) == true
}

func smokePages(for locale: String, pageConfig: PageConfig) -> [String] {
    let configuredPages = pageConfig.smokePages[locale] ?? ["index.html"]
    var seen = Set<String>()
    return configuredPages.filter { seen.insert($0).inserted }
}

func loadReaderPageMeta(bookRoot: URL) throws -> [String: ReaderPageMeta] {
    let metaURL = bookRoot.appendingPathComponent("reader-page-meta.json", isDirectory: false)

    let data: Data
    do {
        data = try Data(contentsOf: metaURL)
    } catch {
        throw BrowserCheckError("Failed to read reader-page-meta.json at \(metaURL.path): \(error.localizedDescription)")
    }

    do {
        return try JSONDecoder().decode([String: ReaderPageMeta].self, from: data)
    } catch {
        throw BrowserCheckError("Failed to decode reader-page-meta.json at \(metaURL.path): \(error.localizedDescription)")
    }
}

func validate(
    snapshot: RuntimeSnapshot,
    relativePath: String,
    locale: String,
    pageConfig: PageConfig,
    pageMeta: ReaderPageMeta?
) throws {
    if pageConfig.skippedPages.contains(relativePath) {
        return
    }

    if snapshot.hasRefreshMeta {
        return
    }

    guard snapshot.readyState == "complete" else {
        throw BrowserCheckError("Expected browser runtime to finish loading \(locale)/\(relativePath), got readyState=\(snapshot.readyState).")
    }

    guard snapshot.hasReaderArticle else {
        throw BrowserCheckError("Expected reader article container on \(locale)/\(relativePath).")
    }

    guard snapshot.hasOutlineElement else {
        throw BrowserCheckError("Expected outline rail container on \(locale)/\(relativePath).")
    }

    if relativePath == "index.html" {
        return
    }

    if snapshot.figureCaptionParagraphCount != 0 {
        throw BrowserCheckError("Expected annotated figure captions to be consumed on \(locale)/\(relativePath), found \(snapshot.figureCaptionParagraphCount) raw caption paragraphs.")
    }

    let figuresEnabled = pageMeta?.referenceSections?.figures != false
    let tablesEnabled = pageMeta?.referenceSections?.tables != false
    let formulasEnabled = pageMeta?.referenceSections?.formulas != false

    if figuresEnabled && snapshot.figureCardCount != snapshot.figureOutlineCount {
        throw BrowserCheckError("Figure outline drift on \(locale)/\(relativePath): cards=\(snapshot.figureCardCount), outlineLinks=\(snapshot.figureOutlineCount).")
    }

    if tablesEnabled && snapshot.tableCardCount != snapshot.tableOutlineCount {
        throw BrowserCheckError("Table outline drift on \(locale)/\(relativePath): cards=\(snapshot.tableCardCount), outlineLinks=\(snapshot.tableOutlineCount).")
    }

    if formulasEnabled && snapshot.formulaCardCount != snapshot.formulaOutlineCount {
        throw BrowserCheckError("Formula outline drift on \(locale)/\(relativePath): cards=\(snapshot.formulaCardCount), outlineLinks=\(snapshot.formulaOutlineCount).")
    }

    let hasVisibleOutlineContent =
        snapshot.headingCount > 0 ||
        (figuresEnabled && snapshot.figureOutlineCount > 0) ||
        (tablesEnabled && snapshot.tableOutlineCount > 0) ||
        (formulasEnabled && snapshot.formulaOutlineCount > 0)

    if hasVisibleOutlineContent {
        if snapshot.outlineHidden != false {
            throw BrowserCheckError("Expected visible outline rail on \(locale)/\(relativePath).")
        }
        if snapshot.bodyClasses.contains("book-outline-empty") {
            throw BrowserCheckError("Expected \(locale)/\(relativePath) to clear book-outline-empty when outline content is visible.")
        }
    } else {
        let preservesOutlineRail =
            snapshot.bodyClasses.contains("book-page-front-matter-outline-rail") ||
            preservesOutlineRail(for: relativePath, locale: locale, pageConfig: pageConfig)

        if !preservesOutlineRail && snapshot.outlineHidden != true {
            throw BrowserCheckError("Expected hidden outline rail on \(locale)/\(relativePath) when no outline content is visible.")
        }
        if !preservesOutlineRail && !snapshot.bodyClasses.contains("book-outline-empty") {
            throw BrowserCheckError("Expected \(locale)/\(relativePath) to keep book-outline-empty when outline content is absent.")
        }
    }

    let expectsFigureFive =
        (locale == "en" && relativePath == "chapters/chapter-05-hydrocarbon-value-chain.html") ||
        (locale == "fr" && relativePath == "chapters/chapter-02-different-phases-of-upstream-oil-and-the-roles-of-states.html")

    if expectsFigureFive {
        guard let figureFive = snapshot.sentinelFigureFive else {
            throw BrowserCheckError("Expected runtime Figure 5 card on \(locale)/\(relativePath).")
        }
        guard figureFive.label == "Figure 5" else {
            throw BrowserCheckError("Expected runtime Figure 5 label on \(locale)/\(relativePath), got \(figureFive.label).")
        }
        guard !figureFive.title.isEmpty else {
            throw BrowserCheckError("Expected runtime Figure 5 title text on \(locale)/\(relativePath).")
        }
    }
}

func runBrowserChecks() throws {
    _ = NSApplication.shared
    NSApplication.shared.setActivationPolicy(.prohibited)

    let config = try parseConfig()
    let publicRoot = config.rootDir.appendingPathComponent("public", isDirectory: true)
    let targets: [(locale: String, bookRoot: URL, publicPathPrefix: String)] = [
        ("en", publicRoot.appendingPathComponent("book", isDirectory: true), "book"),
        ("fr", publicRoot.appendingPathComponent("fr/book", isDirectory: true), "fr/book"),
    ]

    let loader = BrowserPageLoader()

    for target in targets {
        let pageMetaByPath = try loadReaderPageMeta(bookRoot: target.bookRoot)
        let pages: [String]

        if config.scope == "full" {
            pages = try ["index.html"] + sortedChapterPages(bookRoot: target.bookRoot)
        } else {
            pages = smokePages(for: target.locale, pageConfig: config.pageConfig)
        }

        for relativePath in pages {
            let pageURL: URL
            let readAccessURL: URL?

            if let baseURL = config.baseURL {
                let trimmedPrefix = target.publicPathPrefix.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
                let relativeURL = trimmedPrefix + "/" + relativePath
                var components = URLComponents(url: baseURL.appendingPathComponent(relativeURL), resolvingAgainstBaseURL: false)
                components?.queryItems = [URLQueryItem(name: "lang", value: target.locale)]
                pageURL = components?.url ?? baseURL.appendingPathComponent(relativeURL)
                readAccessURL = nil
            } else {
                let fileURL = target.bookRoot.appendingPathComponent(relativePath, isDirectory: false)
                pageURL = localizedFilePageURL(for: fileURL, locale: target.locale)
                readAccessURL = publicRoot
            }

            let snapshot = try loader.snapshot(for: pageURL, readAccessURL: readAccessURL)
            try validate(
                snapshot: snapshot,
                relativePath: relativePath,
                locale: target.locale,
                pageConfig: config.pageConfig,
                pageMeta: pageMetaByPath[relativePath]
            )
        }
    }
}

do {
    try runBrowserChecks()
} catch {
    fputs("\(error)\n", stderr)
    exit(1)
}
