<!DOCTYPE html>
<html>
    <head>
        <title>OGFX - Port Selection</title>
        <link rel="stylesheet" type="text/css" href="/static/index.css">
        <link rel="stylesheet" type="text/css" href="/static/range.css">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <div class="rack">
            <span>Choose a port to connect to:</span>
            <table>
                % index = 0
                % for port in ports:
                    <tr><td><a href="/connect2{{remaining_path}}/{{index}}">{{port.name}}</a></td></tr>
                    % index = index + 1
                %end
        </div>
    </body>
</html>
