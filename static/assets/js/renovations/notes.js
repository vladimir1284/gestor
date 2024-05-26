function getURL(id) {
  return `${globalThis.ContractNotesURL}${id}`;
}

/**
 * @typedef Note
 * */

/**
 * Load contract's notes
 * @param {number} id
 * @returns {Promise<Map<Date, Array<Note>>>}
 * */
async function loadNotes(id) {
  const resp = await fetch(getURL(id));
  if (resp.status != 200) {
    console.error({ status: resp.status, text: resp.statusText });
    throw new Error("Fail to get contract notes");
  }

  return await resp.json();
}

/**
 * Push and reload contract's notes
 * @param {number} id
 * @param {string} content
 * @returns {Promise<Map<Date, Array<Note>>>}
 * */
async function pushNotes(id, content) {
  const resp = await fetch(getURL(id), {
    method: "post",
    body: { content: content },
  });
  if (resp.status != 200) {
    console.error({ status: resp.status, text: resp.statusText });
    throw new Error("Fail to get contract notes");
  }

  return await resp.json();
}

globalThis.loadNotes = loadNotes;
globalThis.pushNotes = pushNotes;
