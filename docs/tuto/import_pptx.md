# PowerPoint Import Tutorial

## Overview

The Presentator system allows you to import existing PowerPoint (.pptx) presentations and convert them into web-based slideshows. This feature extracts content, images, and formatting from your PowerPoint files to create HTML slides compatible with the presentation system.

## Accessing PowerPoint Import

1. Open your web browser and navigate to controller
3. Find the **"Upload PowerPoint"** section

## Import Interface

### Upload Form Elements
- **File Selection**: <img src="../../web/icons/upload.svg" alt="Upload" width="20" height="20" style="vertical-align:middle;"> Choose your .pptx file
- **Slideshow Name**: Automatically filled from filename, or enter custom name
- **Upload Button**: <img src="../../web/icons/upload.svg" alt="Upload" width="20" height="20" style="vertical-align:middle;"> Start the conversion process
- **Status Display**: Shows upload progress and results

## Step-by-Step Import Process

### Step 1: Select PowerPoint File
1. Click **"Choose File"** in the upload section
2. Navigate to your PowerPoint file (.pptx format required)
3. Select the file - **only .pptx files are supported**
4. The slideshow name will auto-fill from the filename

### Step 2: Customize Slideshow Name (Optional)
1. The name field automatically uses your filename
2. Edit the name if you want a different slideshow title
3. Use descriptive names for easy identification later

### Step 3: Upload and Convert
1. Click the <img src="../../web/icons/upload.svg" alt="Upload" width="20" height="20" style="vertical-align:middle;"> **"Upload"** button
2. The button changes to show conversion progress
3. Wait for the conversion process to complete
4. Check the status message for results

## What Gets Converted

### Content Extraction
- **Text Content**: All text from slides with formatting
- **Images**: Pictures and graphics embedded in slides
- **Layouts**: Basic slide structure and positioning
- **Backgrounds**: Solid background colors where possible

### Formatting Preserved
- **Font Sizes**: Relative text sizes maintained
- **Colors**: Text and background colors extracted
- **Basic Formatting**: Bold, italic, and other text styles
- **Lists**: Bullet points and numbered lists

### Not Supported
- **Animations**: PowerPoint animations are not converted
- **Transitions**: Slide transitions are replaced with standard timing
- **Complex Layouts**: Advanced PowerPoint layouts may be simplified
- **Embedded Objects**: Charts, tables may need manual adjustment
- **Slide timings**: Slid timing are automaticly set to 6 seconds
- **Slide layout**: Slide layout could be different than in the pptx

## After Import

### Automatic Integration
- **Slideshow List**: Imported presentation appears in the main slideshow list
- **Network Updates**: All connected viewers receive the updated slideshow list
- **Ready to Use**: Can immediately load and present the imported slideshow

### Post-Import Options
- **Edit Content**: Use the <img src="../../web/icons/edit.svg" alt="Edit" width="20" height="20" style="vertical-align:middle;"> WYSIWYG editor to refine content
- **Adjust Timing**: Modify slide durations as needed
- **Customize Appearance**: Update colors and formatting
- **Add/Remove Slides**: Modify the slideshow structure

## Best Practices

### Before Import
- **Clean Source File**: Review PowerPoint for any issues
- **Simple Layouts**: Complex layouts convert better when simplified
- **Standard Fonts**: Use common fonts for better compatibility
- **Image Quality**: Ensure images are appropriate size and quality

### File Requirements
- **Format**: Only .pptx files (PowerPoint 2007 and newer)
- **Size Limit**: Reasonable file sizes recommended for faster processing
- **Content**: Text-heavy slides convert better than graphics-heavy ones

### After Import Review
- **Check All Slides**: Review each converted slide for accuracy
- **Adjust Timing**: Set appropriate display durations
- **Test Presentation**: Run a preview to ensure everything works
- **Make Edits**: Use the editor to fix any conversion issues

## Troubleshooting

### Common Issues
- **File Not Supported**: Ensure file is .pptx format (not .ppt or other formats)
- **Upload Failed**: Check file size and network connection
- **Missing Content**: Some complex elements may not convert perfectly
- **Formatting Issues**: May require manual adjustment after import

### Error Messages
- **"Please select a PPTX file"**: Wrong file format selected
- **"Upload failed"**: Network or server error during upload
- **"Conversion error"**: Issue processing the PowerPoint file
- **"File too large"**: PowerPoint file exceeds size limits

### Solutions
- **Format Conversion**: Convert .ppt files to .pptx in PowerPoint first
- **File Size**: Compress images in PowerPoint to reduce file size
- **Content Review**: Simplify complex slides before importing
- **Network Check**: Ensure stable connection during upload

---

*This tutorial covers PowerPoint import functionality. For editing imported presentations, see the [WYSIWYG Editor Tutorial](./wysiwyg.md).*
