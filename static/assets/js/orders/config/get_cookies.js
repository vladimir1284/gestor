// @ts-check

/**
 * return a cookie by name
 * @param {string} name
 * @returns {string | null}
 * */
globalThis.getCookie = function (name) {
  if (!document.cookie || document.cookie === "") {
    return null;
  }

  const cookies = document.cookie.split(";");

  for (let cookie of cookies) {
    cookie = cookie.trim();
    if (cookie.substring(0, name.length + 1) === name + "=") {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  return null;
};
