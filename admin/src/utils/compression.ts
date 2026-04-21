export async function compressToURL<T extends object>(obj: T): Promise<string> {
  const str = JSON.stringify(obj);
  const stream = new Blob([str]).stream();
  const compressedStream = stream.pipeThrough(new CompressionStream("deflate"));
  const buffer = await new Response(compressedStream).arrayBuffer();

  // Convert buffer to Base64 (using btoa or a buffer helper)
  return encodeURIComponent(btoa(String.fromCharCode(...new Uint8Array(buffer))));
}

export async function decompressFromURL<T extends object>(base64UriComponent: string): Promise<T> {
  // Restore padding and standard Base64 characters
  const standardBase64 = decodeURIComponent(base64UriComponent);
  const binary = atob(standardBase64);
  const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));

  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(bytes);
      controller.close();
    },
  });

  const decompressedStream = stream.pipeThrough(new DecompressionStream("deflate"));
  const result = await new Response(decompressedStream).text();
  return JSON.parse(result) as T;
}