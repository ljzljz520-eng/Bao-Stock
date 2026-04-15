"""下载 swagger-ui 静态资源，优先国内镜像"""
import os
import sys
import urllib.request

DEST_DIR = sys.argv[1] if len(sys.argv) > 1 else "/swagger-ui"
os.makedirs(DEST_DIR, exist_ok=True)

FILES = {
    "swagger-ui.css": [
        "https://registry.npmmirror.com/swagger-ui-dist/5.18.2/files/swagger-ui.css",
        "https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    ],
    "swagger-ui-bundle.js": [
        "https://registry.npmmirror.com/swagger-ui-dist/5.18.2/files/swagger-ui-bundle.js",
        "https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
    ],
}

for filename, sources in FILES.items():
    dest = os.path.join(DEST_DIR, filename)
    for url in sources:
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"OK: {filename} <- {url}")
            break
        except Exception as e:
            print(f"FAIL: {url} -> {e}")
    else:
        print(f"ERROR: all sources failed for {filename}")
        sys.exit(1)

print("swagger-ui download complete.")
