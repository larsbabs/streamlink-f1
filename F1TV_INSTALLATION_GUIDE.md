# F1TV Plugin Installation and Testing Guide for Ubuntu

This guide will walk you through installing and testing the F1TV plugin on your Ubuntu server.

## Prerequisites

Before you begin, ensure you have:
- Ubuntu server (18.04 or later recommended)
- Python 3.9 or higher
- Git installed
- A valid F1 TV subscription with email and password credentials

## Step 1: Install System Dependencies

First, update your system and install required packages:

```bash
# Update package lists
sudo apt update

# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv git

# Install additional dependencies that streamlink needs
sudo apt install -y libxml2 libxslt1-dev libssl-dev libffi-dev
```

## Step 2: Clone the Repository

Clone this repository with the F1TV plugin:

```bash
# Clone the repository
git clone https://github.com/larsbabs/streamlink-f1.git

# Navigate to the repository
cd streamlink-f1

# Checkout the branch with the F1TV plugin
git checkout copilot/add-f1tv-authentication-plugin
```

## Step 3: Create a Virtual Environment (Recommended)

It's best practice to use a virtual environment to avoid conflicts with system packages:

```bash
# Create a virtual environment
python3 -m venv streamlink-env

# Activate the virtual environment
source streamlink-env/bin/activate

# Your prompt should now show (streamlink-env)
```

## Step 4: Install Streamlink with F1TV Plugin

Install streamlink in development mode, which includes the F1TV plugin:

```bash
# Install streamlink in editable mode with all dependencies
pip install -e .

# This will install streamlink and the F1TV plugin
```

Alternatively, if you encounter issues, install dependencies manually:

```bash
# Install core dependencies
pip install certifi isodate lxml pycountry pycryptodome PySocks requests trio trio-websocket urllib3 websocket-client

# Install streamlink in editable mode
pip install -e .
```

## Step 5: Verify Installation

Check that streamlink is installed correctly and the F1TV plugin is available:

```bash
# Check streamlink version
streamlink --version

# List all available plugins (should include f1tv)
streamlink --plugins

# Check if f1tv plugin is specifically available
streamlink --plugin-dir src/streamlink/plugins --plugins | grep f1tv
```

## Step 6: Test the F1TV Plugin

### Test 1: Basic URL Matching

Test if the plugin recognizes F1TV URLs:

```bash
# This should show the f1tv plugin is matched
streamlink --loglevel debug https://f1tv.formula1.com/ 2>&1 | grep -i "loaded plugin"
```

### Test 2: List Available Streams (Without Authentication)

Try listing streams without authentication to see the error message:

```bash
streamlink https://f1tv.formula1.com/detail/1000000012
```

You should see an error message indicating authentication is required.

### Test 3: Authenticate and List Streams

**IMPORTANT:** Replace `your-email@example.com` and `your-password` with your actual F1 TV credentials:

```bash
# List available stream qualities for a specific content
streamlink \
  --f1tv-email="your-email@example.com" \
  --f1tv-password="your-password" \
  https://f1tv.formula1.com/detail/1000000012
```

If authentication is successful, you should see available stream qualities like:
```
Available streams: 360p, 540p, 720p, 1080p (worst, best)
```

### Test 4: Stream to a Video Player

To actually watch a stream (requires VLC or another video player):

```bash
# Install VLC if you don't have it
sudo apt install -y vlc

# Stream to VLC
streamlink \
  --f1tv-email="your-email@example.com" \
  --f1tv-password="your-password" \
  --player vlc \
  https://f1tv.formula1.com/detail/1000000012 best
```

### Test 5: Save Stream to File

To save a stream to a file instead of playing it:

```bash
# Save the stream to a file
streamlink \
  --f1tv-email="your-email@example.com" \
  --f1tv-password="your-password" \
  --output race.mp4 \
  https://f1tv.formula1.com/detail/1000000012 best

# Monitor the download progress
# Press Ctrl+C to stop
```

## Step 7: Run Unit Tests (Optional)

If you want to verify the plugin code is working correctly:

```bash
# Install test dependencies
pip install pytest pytest-trio freezegun requests-mock

# Run the F1TV plugin tests
pytest tests/plugins/test_f1tv.py -v

# You should see output like:
# test_can_handle_url_positive PASSED
# test_can_handle_url_negative PASSED
```

## Step 8: Advanced Testing with Debug Logging

For troubleshooting, enable debug logging to see detailed information:

```bash
streamlink \
  --loglevel debug \
  --f1tv-email="your-email@example.com" \
  --f1tv-password="your-password" \
  https://f1tv.formula1.com/detail/1000000012 best \
  2>&1 | tee debug.log

# This saves debug output to debug.log file for review
```

## Step 9: Create Configuration File (Optional)

To avoid typing credentials every time, create a configuration file:

```bash
# Create streamlink config directory
mkdir -p ~/.config/streamlink

# Create config file
cat > ~/.config/streamlink/config << 'EOF'
# F1TV credentials
f1tv-email=your-email@example.com
f1tv-password=your-password

# Default player
player=vlc

# Default quality
default-stream=best
EOF

# Secure the config file
chmod 600 ~/.config/streamlink/config
```

Now you can use streamlink without specifying credentials:

```bash
streamlink https://f1tv.formula1.com/detail/1000000012
```

## Common Issues and Solutions

### Issue 1: "No plugin can handle URL"
**Solution:** Make sure you're using a valid F1TV URL starting with `https://f1tv.formula1.com/`

### Issue 2: "Authentication failed"
**Solution:** 
- Verify your F1 TV credentials are correct
- Check if your F1 TV subscription is active
- Ensure you have internet connectivity

### Issue 3: "Module not found" errors
**Solution:** Make sure you activated the virtual environment and installed all dependencies:
```bash
source streamlink-env/bin/activate
pip install -e .
```

### Issue 4: Stream quality not available
**Solution:** Not all content may be available in all qualities. Try different quality options:
```bash
streamlink --f1tv-email=... --f1tv-password=... URL 720p
```

## Deactivating the Virtual Environment

When you're done, deactivate the virtual environment:

```bash
deactivate
```

## Making the Plugin Available System-Wide (Optional)

If you want to install streamlink system-wide instead of in a virtual environment:

```bash
# Exit the virtual environment if active
deactivate

# Install system-wide (requires sudo)
sudo pip3 install -e /path/to/streamlink-f1
```

## Summary of Key Commands

Quick reference for daily use:

```bash
# Activate environment
source streamlink-env/bin/activate

# Watch live F1 stream
streamlink --f1tv-email=EMAIL --f1tv-password=PASS https://f1tv.formula1.com/live best

# List available streams
streamlink --f1tv-email=EMAIL --f1tv-password=PASS https://f1tv.formula1.com/detail/ID

# Save to file
streamlink --f1tv-email=EMAIL --f1tv-password=PASS -o output.mp4 URL best
```

## Next Steps

- Explore other F1TV content by visiting https://f1tv.formula1.com/
- Check out other streamlink plugins: `streamlink --plugins`
- Read the full streamlink documentation: https://streamlink.github.io/

## Support

If you encounter issues:
1. Check the debug logs: `streamlink --loglevel debug ...`
2. Verify your F1 TV subscription is active
3. Open an issue on the GitHub repository with debug logs

---

**Note:** You must have an active F1 TV subscription to use this plugin. The plugin does not provide free access to F1 TV content.
