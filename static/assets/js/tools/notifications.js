// @ts-check

/** @type {import('alpinejs').default} */
var Alpine;

/**
 * @typedef NotificationMSG
 * @property {string} title
 * @property {string} msg
 * @property {string} [icon]
 * @property {string} [status]
 * */

/** @type {Array<NotificationMSG>}*/
const _nots = [];

/**
 * Show a notification
 * @param {string} title
 * @param {string} msg
 * @param {string} [icon]
 * @param {string} [status]
 * */
function notify(title, msg, icon, status) {
  showNotify({
    title,
    msg,
    icon,
    status,
  });
}

/**
 * Show a notification
 * @param {NotificationMSG} not
 * */
function showNotify(not) {
  const nots = Alpine.store("notifications");
  if (nots) {
    nots.notify(not);
  } else {
    _nots.push(not);
  }
}

globalThis.notify = notify;
globalThis.showNotify = showNotify;

function notStore() {
  return {
    /** @type {Array<NotificationMSG>}*/
    nots: [],

    init() {
      _nots.forEach((e) => {
        this.notify(e);
      });
    },

    /**
     * Remove a notification
     * @param {NotificationMSG} not
     * */
    remove(not) {
      const idx = this.nots.indexOf(not);
      if (idx != -1) this.nots.splice(idx, 1);
    },

    /**
     * Show a notification
     * @param {NotificationMSG} not
     * */
    notify(not) {
      if (!not.icon) {
        not.icon = "bxs-info-circle";
      }
      if (!not.status) {
        not.status = "primary";
      }
      this.nots.push(not);
      setTimeout(() => {
        this.remove(not);
      }, 5000);
    },
  };
}

document.addEventListener("alpine:init", () => {
  Alpine.store("notifications", notStore());
});
