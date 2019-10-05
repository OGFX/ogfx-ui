<!DOCTYPE html>
<html>
    <head>
        <title>OGFX - Upload a file</title>
        <link rel="stylesheet" type="text/css" href="/static/index.css">
        <link rel="stylesheet" type="text/css" href="/static/range.css">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <div class="rack">
            <span>Upload a file</span>
            <form action="/upload2{{remaining_path}}" method="post" enctype="multipart/form-data">
                <input type="file" id="file-selection" name="upload">
                <input type="submit" value="submit">
            </form>
        </div>
    </body>
</html>
