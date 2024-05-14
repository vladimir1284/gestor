// @ts-check

import { url } from "./config_url.js";

/**
 * @returns {Promise<Map<string, string>>}
 * */
export async function getOptions() {
  const resp = await fetch(url);
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
