$port = 8080
$root = Join-Path $PSScriptRoot "public"
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
$listener.Start()

$mimeTypes = @{
    ".html" = "text/html; charset=utf-8"
    ".css"  = "text/css"
    ".js"   = "application/javascript"
    ".json" = "application/json"
    ".png"  = "image/png"
    ".jpg"  = "image/jpeg"
    ".svg"  = "image/svg+xml"
    ".ico"  = "image/x-icon"
}

Write-Host "Server running at http://localhost:$port" -ForegroundColor Green
Write-Host "  index  -> http://localhost:$port/index.html" -ForegroundColor Cyan
Write-Host "  admin  -> http://localhost:$port/admin.html" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray

Start-Process "http://localhost:$port/index.html"

while ($listener.IsListening) {
    $context  = $listener.GetContext()
    $request  = $context.Request
    $response = $context.Response

    $urlPath = $request.Url.LocalPath
    if ($urlPath -eq "/") { $urlPath = "/index.html" }

    $filePath = Join-Path $root ($urlPath.TrimStart("/").Replace("/", [System.IO.Path]::DirectorySeparatorChar))

    if (Test-Path $filePath -PathType Leaf) {
        $ext   = [System.IO.Path]::GetExtension($filePath)
        $mime  = if ($mimeTypes.ContainsKey($ext)) { $mimeTypes[$ext] } else { "application/octet-stream" }
        $bytes = [System.IO.File]::ReadAllBytes($filePath)
        $response.ContentType      = $mime
        $response.ContentLength64  = $bytes.Length
        $response.StatusCode       = 200
        $response.OutputStream.Write($bytes, 0, $bytes.Length)
        Write-Host "200  $urlPath" -ForegroundColor Green
    } else {
        $msg  = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found: $urlPath")
        $response.ContentType      = "text/plain"
        $response.StatusCode       = 404
        $response.ContentLength64  = $msg.Length
        $response.OutputStream.Write($msg, 0, $msg.Length)
        Write-Host "404  $urlPath" -ForegroundColor Red
    }

    $response.OutputStream.Close()
}
