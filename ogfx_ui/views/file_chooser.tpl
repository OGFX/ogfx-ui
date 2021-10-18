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
                % import urllib
                % index = 0
                % for file in files:
                <tr>
                  <td><a href="/load2{{remaining_path}}/{{urllib.parse.quote(file, safe='')}}">{{file}}</a></td>
                </tr>
                % index = index + 1
                % end
             </table>
        </div>
    </body>
</html>
