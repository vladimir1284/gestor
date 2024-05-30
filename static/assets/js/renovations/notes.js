function getURL(id) {
  return `${globalThis.ContractNotesURL}${id}`;
}

/**
 * @typedef Note
 * */
/**
 * @typedef NoteGroup
 * @property {Date} date
 * @property {string} strDate
 * @property {Array<Note>} notes
 * */

/**
 * Preprocess Notes
 * @param {Array<NoteGroup>} notes
 * @returns {Array<NoteGroup>}
 * */
function processNotes(notes) {
  for (let note of notes) {
    const date = new Date(note.date);
    note.date = date;
    const strDate = date.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
    note.strDate = strDate;
  }
  return notes;
}

/**
 * Load contract's notes
 * @param {number} id
 * @returns {Promise<Array<NoteGroup>>}
 * */
async function loadNotes(id) {
  const resp = await fetch(getURL(id));
  if (resp.status != 200) {
    console.error({ status: resp.status, text: resp.statusText });
    throw new Error("Fail to get contract notes");
  }

  const notes = await resp.json();
  return processNotes(notes);
}

/**
 * Push and reload contract's notes
 * @param {number} id
 * @param {string} content
 * @returns {Promise<Array<NoteGroup>>}
 * */
async function pushNotes(id, content) {
  const data = new FormData();
  data.set("content", content);
  const resp = await fetch(getURL(id), {
    method: "post",
    body: data,
  });
  if (resp.status != 200) {
    console.error({ status: resp.status, text: resp.statusText });
    throw new Error("Fail to get contract notes");
  }

  const notes = await resp.json();
  return processNotes(notes);
}

globalThis.loadNotes = loadNotes;
globalThis.pushNotes = pushNotes;
