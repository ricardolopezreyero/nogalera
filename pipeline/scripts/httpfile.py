"""Archivo remoto de solo lectura con peticiones HTTP Range (para pyarrow)."""
import io, time, urllib.request, urllib.error

class HTTPRangeFile(io.RawIOBase):
    def __init__(self, url, size=None, block=1 << 20):
        self.url, self.pos, self.block = url, 0, block
        self.cache = {}
        if size is None:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=60) as r:
                size = int(r.headers["Content-Length"])
        self.size = size
        self.bytes_fetched = 0

    def readable(self): return True
    def seekable(self): return True
    def tell(self): return self.pos
    def seek(self, off, whence=0):
        if whence == 0: self.pos = off
        elif whence == 1: self.pos += off
        else: self.pos = self.size + off
        return self.pos

    def _get(self, start, end):  # inclusive end
        for attempt in range(6):
            try:
                req = urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{end}"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = r.read()
                self.bytes_fetched += len(data)
                return data
            except Exception as e:
                if attempt == 5: raise
                time.sleep(2 ** attempt)

    def read(self, n=-1):
        if n is None or n < 0: n = self.size - self.pos
        n = min(n, self.size - self.pos)
        if n <= 0: return b""
        start, end = self.pos, self.pos + n - 1
        if n >= self.block:
            data = self._get(start, end)
        else:
            # lectura pequeña: usa bloques alineados en caché
            b0, b1 = start // self.block, end // self.block
            parts = []
            for b in range(b0, b1 + 1):
                if b not in self.cache:
                    bs = b * self.block
                    self.cache[b] = self._get(bs, min(bs + self.block, self.size) - 1)
                parts.append(self.cache[b])
            buf = b"".join(parts)
            off = start - b0 * self.block
            data = buf[off:off + n]
        self.pos += len(data)
        return data

    def readinto(self, b):
        data = self.read(len(b))
        b[:len(data)] = data
        return len(data)
