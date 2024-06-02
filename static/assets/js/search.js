// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

/**
 * Search for match
 * @param {string} text
 * @param {string} query
 * @returns {boolean}
 * */
function match(text, query) {
  const textUC = text.toUpperCase();
  const queries = query.toUpperCase().split(" ");
  for (let q of queries) {
    if (textUC.search(q) == -1) {
      return false;
    }
  }
  return true;
}

/**
 * Return a highlighted html string
 * @param {string} text
 * @param {string} query
 * @returns {string}
 * */
function highlightMatch(text, query) {
  if (query == "") return text;

  const textUC = text.toUpperCase();
  const queries = query.toUpperCase().split(" ");
  const idxs = [];

  // Search match index (start, end)
  for (let q of queries) {
    if (q.length == 0) continue;

    let start = 0;
    let end = 0;

    while (start != -1) {
      start = textUC.indexOf(q, end);
      end = start + q.length;

      if (start == -1) break;

      idxs.push({
        start,
        end,
      });
    }
  }

  if (idxs.length == 0) return text;

  // Sort by starts
  idxs.sort((a, b) => {
    return a.start - b.start;
  });

  // Merge where collide
  for (let i = 0; i < idxs.length - 1; i++) {
    const a = idxs[i];
    const b = idxs[i + 1];
    if (b.start < a.end) {
      if (a.end < b.end) a.end = b.end;
      idxs.splice(i + 1, 1);
      i--;
    }
  }

  let result = "";
  let lastend = 0;
  for (let idx of idxs) {
    const prev = text.substring(lastend, idx.start);
    const match = text.substring(idx.start, idx.end);
    lastend = idx.end;
    result += `${prev}<span class="match">${match}</span>`;
  }
  result += text.substring(lastend);

  return result;
}

document.addEventListener("alpine:init", () => {
  Alpine.store("search", {
    search: "",
  });
});

globalThis.match = match;
globalThis.highlightMatch = highlightMatch;
