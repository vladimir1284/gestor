async function loadGOWasm(url) {
  const go = new Go();
  try {
    const resp = await fetch(url);
    const source = await resp.arrayBuffer();
    const result = await WebAssembly.instantiate(source, go.importObject);
    await go.run(result.instance);
  } catch (e) {
    console.error(e);
  }
}
