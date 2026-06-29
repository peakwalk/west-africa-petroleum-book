const VOID_TAGS = new Set([
  "area",
  "base",
  "br",
  "col",
  "embed",
  "hr",
  "img",
  "input",
  "link",
  "meta",
  "param",
  "source",
  "track",
  "wbr",
]);

function normalizeText(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

function stripHtmlTags(html) {
  return normalizeText(String(html || "").replace(/<[^>]+>/g, " "));
}

function isNarrativeFigureReference(text) {
  return /^Figures?\s+\d+(?:(?:\s*,\s*|\s+and\s+|\s+to\s+|\s*-\s*)(?:Figures?\s+)?\d+)*\s+(?:show|shows|illustrate|illustrates|present|presents|depict|depicts|contain|contains)\b/i.test(
    normalizeText(text)
  );
}

function parseFigureCaption(text) {
  const normalized = normalizeText(text);

  if (isNarrativeFigureReference(normalized)) {
    return null;
  }

  const match = normalized.match(/^Figure\s+0*(\d+)(?:\s*:\s*|\s+)(.*)$/i);

  if (!match) {
    return null;
  }

  return {
    number: String(Number(match[1])),
    title: normalizeText(match[2] || ""),
  };
}

function parseFigureNumber(text) {
  const match = normalizeText(text).match(/^Figure\s+0*(\d+)\b/i);
  return match ? String(Number(match[1])) : "";
}

function isLikelyAltDerivedCaption(text) {
  const normalized = normalizeText(text);

  if (!normalized) {
    return false;
  }

  if (/^(Figure|Table|Chapter|Chapitre|Section)\b/i.test(normalized)) {
    return false;
  }

  return normalized.split(/\s+/).length <= 24;
}

function findTagEnd(source, startIndex) {
  let index = startIndex + 1;
  let quote = "";

  while (index < source.length) {
    const char = source[index];

    if (quote) {
      if (char === quote) {
        quote = "";
      }
      index += 1;
      continue;
    }

    if (char === '"' || char === "'") {
      quote = char;
      index += 1;
      continue;
    }

    if (char === ">") {
      return index + 1;
    }

    index += 1;
  }

  return source.length;
}

function parseTagToken(source, startIndex) {
  if (source.startsWith("<!--", startIndex)) {
    const endIndex = source.indexOf("-->", startIndex + 4);
    return {
      nextIndex: endIndex === -1 ? source.length : endIndex + 3,
      type: "comment",
    };
  }

  const tagEnd = findTagEnd(source, startIndex);
  const rawTag = source.slice(startIndex, tagEnd);
  const isClosingTag = /^<\s*\//.test(rawTag);

  if (/^<\s*[!?]/.test(rawTag)) {
    return {
      nextIndex: tagEnd,
      type: "special",
    };
  }

  const nameMatch = rawTag.match(/^<\s*\/?\s*([a-zA-Z0-9:-]+)/);
  const tagName = nameMatch ? nameMatch[1].toLowerCase() : "";
  const selfClosing = !isClosingTag && (VOID_TAGS.has(tagName) || /\/\s*>$/.test(rawTag));

  return {
    name: tagName,
    nextIndex: tagEnd,
    selfClosing,
    type: isClosingTag ? "end" : "start",
  };
}

function collectTopLevelBlocks(articleHtml) {
  const source = String(articleHtml || "");
  const blocks = [];
  let currentStart = -1;
  let currentTagName = "";
  let depth = 0;
  let index = 0;

  while (index < source.length) {
    const tagIndex = source.indexOf("<", index);

    if (tagIndex === -1) {
      break;
    }

    const token = parseTagToken(source, tagIndex);
    index = token.nextIndex;

    if (token.type === "comment" || token.type === "special" || !token.name) {
      continue;
    }

    if (token.type === "start") {
      if (depth === 0) {
        currentStart = tagIndex;
        currentTagName = token.name;
      }

      if (token.selfClosing) {
        if (depth === 0) {
          const html = source.slice(currentStart, token.nextIndex);
          blocks.push({
            html,
            tagName: currentTagName,
            text: stripHtmlTags(html),
          });
          currentStart = -1;
          currentTagName = "";
        }
        continue;
      }

      depth += 1;
      continue;
    }

    if (depth === 0) {
      continue;
    }

    depth -= 1;

    if (depth === 0 && currentStart !== -1) {
      const html = source.slice(currentStart, token.nextIndex);
      blocks.push({
        html,
        tagName: currentTagName,
        text: stripHtmlTags(html),
      });
      currentStart = -1;
      currentTagName = "";
    }
  }

  return blocks;
}

function getFigureNumberFromMediaHtml(html) {
  return Array.from(String(html || "").matchAll(/\balt="([^"]*)"/gi))
    .map(function (match) {
      return parseFigureNumber(match[1]);
    })
    .find(Boolean) || "";
}

function collectRuntimeFigureEntries(articleHtml) {
  const article = String(articleHtml || "");
  const blocks = collectTopLevelBlocks(article);
  const figures = [];

  for (let index = 0; index < blocks.length; index += 1) {
    const block = blocks[index];
    const explicitCaption = parseFigureCaption(block.text);

    if (block.tagName !== "p") {
      continue;
    }

    if (explicitCaption) {
      figures.push(explicitCaption);
      continue;
    }

    if (!isLikelyAltDerivedCaption(block.text)) {
      continue;
    }

    const mediaCandidates = [];
    let previousIndex = index - 1;

    while (
      previousIndex >= 0 &&
      blocks[previousIndex].tagName === "p" &&
      /<img\b/i.test(blocks[previousIndex].html)
    ) {
      mediaCandidates.unshift(blocks[previousIndex]);
      previousIndex -= 1;
    }

    if (!mediaCandidates.length) {
      continue;
    }

    const figureNumber = mediaCandidates
      .map(function (candidate) {
        return getFigureNumberFromMediaHtml(candidate.html);
      })
      .find(Boolean);

    if (figureNumber) {
      figures.push({
        number: figureNumber,
        title: normalizeText(block.text),
      });
    }
  }

  return figures;
}

export function collectRuntimeFigureNumbers(articleHtml) {
  return collectRuntimeFigureEntries(articleHtml).map(function (figure) {
    return figure.number;
  });
}

export function countRuntimeFigures(articleHtml) {
  const article = String(articleHtml || "");
  return (article.match(/class="[^"]*figure-card[^"]*"/gi) || []).length + collectRuntimeFigureEntries(article).length;
}

export function countRuntimeTables(articleHtml) {
  const article = String(articleHtml || "");
  return (article.match(/class="[^"]*table-anchor-target[^"]*"/gi) || []).length + (article.match(/<table\b/gi) || []).length;
}

export function countRuntimeFormulas(articleHtml) {
  const article = String(articleHtml || "");
  return (article.match(/class="[^"]*formula-anchor-target[^"]*"/gi) || []).length + (article.match(/\bdata-equation-label\s*=/gi) || []).length;
}
