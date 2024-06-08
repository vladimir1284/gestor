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

globalThis.bindShortcut = _bindShortCut;

function initShortCuts() {
  window.addEventListener("keyup", (e) => {
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
    shortcut += e.key.toLowerCase();

    const funcs = shortcutMap.get(shortcut);
    if (funcs && funcs?.length > 0) {
      for (let func of funcs) {
        const ret = func(e);
        if (ret === true) {
          break;
        }
      }
    } else {
      console.log({
        msg: "Not binded found for this shortcut",
        shortcut,
        event: e,
      });
    }
  });
}

window.addEventListener("load", initShortCuts);
