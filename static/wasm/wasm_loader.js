async function loadGOWasm(url) {
  // if (!WebAssembly.instantiateStreaming) {
  //   WebAssembly.instantiateStreaming = async (resp, importObject) => {
  //     const source = await (await resp).arrayBuffer();
  //     return await WebAssembly.instantiate(source, importObject);
  //   };
  // }
  const resp = await fetch(url);
  const source = await resp.arrayBuffer();
  const go = new Go();
  try {
    const result = await WebAssembly.instantiate(source, go.importObject);
    // const result = await WebAssembly.instantiateStreaming(
    //   fetch(url),
    //   go.importObject,
    // );
    await go.run(result.instance);
  } catch (e) {
    console.error(e);
  }
}
