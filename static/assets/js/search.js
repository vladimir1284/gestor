// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

// Match methods

/**
 * Search for match
 * Search letter order don't care about words match
 * @param {string} text
 * @param {string} query
 * @returns {boolean}
 * */
function letterMatch(text, query) {
  text = text.toUpperCase();
  query = query.toUpperCase().replace(" ", "");

  let index = 0;
  for (let letter of query) {
    index = text.indexOf(letter, index);
    if (index === -1) {
      return false;
    }
  }
  return true;
}

/**
 * Search for match
 * Search for words
 * @param {string} text
 * @param {string} query
 * @returns {boolean}
 * */
function wordMatch(text, query) {
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
 * Search for match
 * Search for words
 * @param {string} text - the text to search for matches
 * @param {string} query - the query
 * @returns {number} - Match type order by match importance
 * where -1 is no match,
 * 0 is the most important match,
 * 1 is less important than 0,
 * 2 is less important than 1...
 * */
function _advanceMatch(text, query) {
  text = text.toUpperCase();
  query = query.toUpperCase();

  const textNS = text.replace(" ", "");
  const queryNS = query.replace(" ", "");

  if (textNS === queryNS) {
    return 0;
  }

  if (textNS.indexOf(queryNS) !== -1) {
    return 1;
  }

  if (wordMatch(text, query)) {
    return 2;
  }

  if (letterMatch(text, query)) {
    return 3;
  }

  return -1;
}

// Highlight Methods

/**
 * Return a highlighted html string for the letters matches
 * @param {string} text
 * @param {string} query
 * @returns {string}
 * */
function highlightLetterMatch(text, query) {
  if (query == "") return text;

  const textUC = text.toUpperCase();
  const queries = query.toUpperCase().replace(" ", "");
  const idxs = [];

  // Search match index (start, end)
  let start = 0;
  for (let q of queries) {
    start = textUC.indexOf(q, start);
    idxs.push({
      start,
      end: start + 1,
    });
  }

  if (idxs.length == 0) return text;

  // Merge where collide
  for (let i = 0; i < idxs.length - 1; i++) {
    const a = idxs[i];
    const b = idxs[i + 1];
    if (b.start <= a.end) {
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

/**
 * Return a highlighted html string for the words matches
 * @param {string} text
 * @param {string} query
 * @returns {string}
 * */
function highlightWordMatch(text, query) {
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

/**
 * Return a highlighted html string for the words matches
 * @param {string} text
 * @param {string} query
 * @param {number} [type]
 * @returns {string}
 * */
function _advanceHighlightMatch(text, query, type) {
  if (type === undefined) {
    type = advanceMatch(text, query);
  }
  if (type === 0) {
    return `<span class="match">${text}</span>`;
  }

  if (type === 1) {
    const start = findRealIndex(text, query);
    const end = findRealEndIndex(text, query, start);
    const pre = text.substring(0, start);
    const mid = text.substring(start, end);
    const suf = text.substring(end);
    return `${pre}<span class="match">${mid}</span>${suf}`;
  }

  if (type === 2) {
    return highlightWordMatch(text, query);
  }

  if (type === 3) {
    return highlightLetterMatch(text, query);
  }

  return text;
}

// tools

/**
 * Return the real index of a match counting space but ignore them on the match
 * @param {string} text
 * @param {string} query
 * @returns {number}
 * */
function findRealIndex(text, query) {
  const qNS = query.replace(" ", "").toUpperCase();
  text = text.toUpperCase();
  for (let i = 0; i < text.length - 1; i++) {
    const sub = text.substring(i).replace(" ", "");
    if (sub.indexOf(qNS) == 0) {
      return i;
    }
  }
  return -1;
}

/**
 * Return the real index in a text of the query length
 * ignoring the space on the match but counting them on the index
 * @param {string} text
 * @param {string} query
 * @param {number} start
 * @returns {number}
 * */
function findRealEndIndex(text, query, start) {
  let index = start;
  for (let i = 0; i < query.replace(" ", "").length; i++) {
    if (text.charAt(index) === " ") {
      index++;
    }
    index++;
  }
  return index;
}

document.addEventListener("alpine:init", () => {
  Alpine.store("search", {
    search: "",
  });
});

globalThis.match = wordMatch;
globalThis.highlightMatch = highlightWordMatch;

/**
 * Search for match
 * Search for words
 * @param {string} text - the text to search for matches
 * @param {string} query - the query
 * @returns {number} - Match type order by match importance
 * where -1 is no match,
 * 0 is the most important match,
 * 1 is less important than 0,
 * 2 is less important than 1...
 * */
function advanceMatch(text, query) {
  try {
    // Use WASM function fastest
    return AdvanceMatch(text, query);
  } catch (e) {
    // If wasm fail for some reason use JS slower
    return _advanceMatch(text, query);
  }
}
/**
 * Return a highlighted html string for the words matches
 * @param {string} text
 * @param {string} query
 * @param {number} [type]
 * @returns {string}
 * */
function advanceHighlightMatch(text, query, type) {
  try {
    // Use WASM function fastest
    return AdvanceHighlightMatch(text, query, type);
  } catch (e) {
    // If wasm fail for some reason use JS slower
    return _advanceHighlightMatch(text, query, type);
  }
}
globalThis.advanceMatch = advanceMatch;
globalThis.advanceHighlightMatch = advanceHighlightMatch;
