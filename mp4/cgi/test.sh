html=""


html+=$(cat << EOF
    <!DOCTYPE html>
    <html>
    <head><link rel="stylesheet" href="http://localhost/nytest.css"><title>diktbase</title></head>
    <body>
    <div class="topdiv">
        <h1 class="headline">Gruppe 12 sin diktbase</h1>
EOF
)

echo $html
