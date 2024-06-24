// @ts-check

/** @type {Map<string, Function[]>} */
const shortcutMap = new Map();

/**
 * Bind a shortcut to a function
 * @param {string} shortcut - Keys for the shortcut, example: ctrl+b or alt+b or ctrl+alt+shift+b
 * @param {Function} func - The function to execute on shortcut recognized
 * @param {boolean} [override] - Override the previous shortcuts bind to this keys combination or keep them
 * */
function _bindShortCut(shortcut, func, override = false) {
  shortcut = shortcut.toLowerCase();
  if (override) {
    shortcutMap.set(shortcut, [func]);
  }
  const funcs = shortcutMap.get(shortcut);
  if (funcs) {
    funcs.push(func);
  } else {
    shortcutMap.set(shortcut, [func]);
  }
}

/**
 * Bind a shortcut or a list of shortcuts to a function
 * @param {string | string[]} shortcuts - Keys for the shortcut, example: ctrl+b or alt+b or ctrl+alt+shift+b
 * @param {Function} func - The function to execute on shortcut recognized
 * @param {boolean} [override] - Override the previous shortcuts bind to this keys combination or keep them
 * */
function _bindShortsCut(shortcuts, func, override = false) {
  if (shortcuts instanceof Array) {
    for (let sc of shortcuts) {
      _bindShortCut(sc, func, override);
    }
    return;
  }

  _bindShortCut(shortcuts, func, override);
}

globalThis.bindShortcut = _bindShortsCut;

function initShortCuts() {
  window.addEventListener("keydown", (e) => {
    let shortcut = "";
    if (e.ctrlKey) {
      shortcut += "ctrl+";
    }
    if (e.altKey) {
      shortcut += "alt+";
    }
    if (e.shiftKey) {
      shortcut += "shift+";
    }
    let key = e.key.toLowerCase();
    if (key === " ") {
      key = "space";
    }

    shortcut += key;

    if (globalThis.keyboard) {
      console.log(shortcut);
    }

    const funcs = shortcutMap.get(shortcut);
    if (funcs && funcs?.length > 0) {
      for (let func of funcs) {
        const ret = func(e);
        if (ret === true) {
          break;
        }
      }
    }
  });
}

window.addEventListener("load", initShortCuts);
