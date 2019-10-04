<!DOCTYPE html>
<html>
    <head>
        <title>OGFX - Upload a file</title>
    </head>
    <body>
        <form action="/upload2{{remaining_path}}" method="post" enctype="multipart/form-data">
            <input type="file" id="file-selection" name="upload">
            <label for="file-selection">Select a file..."</label>
            <input type="submit" value="submit">
        </form>
    </body>
</html>
