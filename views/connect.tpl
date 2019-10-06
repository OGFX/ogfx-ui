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
            <form action="/connect2{{remaining_path}}" method="post" enctype="multipart/form-data">
                % for port in ports:
                    <p><input type="radio" name="port" value="{{port.name}}">{{port.name}}</p>
                %end
                <input type="submit" value="submit">
            </form>
        </div>
    </body>
</html>
