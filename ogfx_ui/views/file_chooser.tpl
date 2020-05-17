<!DOCTYPE html>
<html>
    <head>
        <title>OGFX - File Selection</title>
        <link rel="stylesheet" type="text/css" href="/static/index.css">
        <link rel="stylesheet" type="text/css" href="/static/range.css">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <div class="rack">
            <span>Choose a file:</span>
            <table>
                % index = 0
                % for file in files:
                <tr>
                  <td><a href="/select_file2{{remaining_path}}/{{file['name']}}">{{file['name']}}</a></td>
                  <td>[{{file['size']}}]</td>
                  <td>[{{file['date']}}]</td>
                  <td>[{{port['output']}}]</td>
                </tr>
                % index = index + 1
                % end
             </table>
        </div>
    </body>
</html>
