# Test Assets

This folder contains test files for API testing.

## Files:
- `sample-painting.jpg` - A sample image for testing painting uploads
- You can replace this with any JPEG image file for testing

## Usage:
The HTTP test file (`api-tests.http`) references files in this directory for multipart form uploads.

## Note:
Since we can't create binary image files through text, you'll need to:
1. Add a real JPEG image file named `sample-painting.jpg` to this folder
2. Or modify the HTTP test file to point to an existing image on your system
