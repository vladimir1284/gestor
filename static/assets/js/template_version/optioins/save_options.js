// @ts-check

import { url } from "./config_url.js";

/**
 * @param {Map<string, string>} options
 * @returns {Promise<Map<string, string>>}
 * */
export async function saveOptions(options) {
  const resp = await fetch(url, {
    method: "POST",
    body: options,
  });

  if (resp.status != 200) {
    console.error({
      status: resp.status,
      statusText: resp.statusText,
      text: await resp.text(),
    });
  }
  const data = await resp.json();
  return data;
}
