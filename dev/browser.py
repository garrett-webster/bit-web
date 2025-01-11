import webbrowser
import tempfile

# Define HTML content with JavaScript to open a new window of specified size
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Open New Window</title>
    <script type="text/javascript">
        function openNewWindow() {
            window.open('', '', 'width=800,height=600'); // Set desired width and height
        }
        window.onload = openNewWindow;
    </script>
</head>
<body>
    <h1>Opening New Window...</h1>
</body>
</html>
"""

# Create a temporary HTML file
with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as temp_file:
    temp_file.write(html_content)
    temp_file_path = temp_file.name

# Open the temporary HTML file in the default web browser
webbrowser.open(f'file://{temp_file_path}')
