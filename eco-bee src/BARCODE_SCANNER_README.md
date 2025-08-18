# Barcode Scanner with Mistral Pixtral

## Overview

The EcoBee application now includes an advanced barcode scanner powered by Mistral's Pixtral vision model. This allows users to scan barcodes using their camera or by uploading images, extracting product information and sustainability insights.

## Features

- 📱 **Camera Scanning**: Use device camera to scan barcodes in real-time
- 🖼️ **Image Upload**: Upload existing images containing barcodes
- 🔍 **Smart Detection**: Uses Mistral Pixtral to detect and analyze barcodes
- 🌱 **Sustainability Insights**: Identifies eco-friendly labels and certifications
- 📊 **Product Information**: Extracts product names, brands, and categories

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Get Mistral API Key

1. Visit [Mistral Console](https://console.mistral.ai/)
2. Create an account or sign in
3. Generate an API key
4. Set the environment variable:

## Usage

### Frontend Integration

The barcode scanner is integrated into the IntakeForm component:

1. Navigate to the "Outfit" step in the form
2. Click the barcode icon (📊) next to the barcode input field
3. Choose to either:
   - **Use Camera**: Scan barcodes directly with your device camera
   - **Upload Image**: Select an image file containing a barcode

### API Endpoints

#### Scan Barcode

**POST** `/api/scan-barcode`

**Multipart Form Data:**

```
image: [image file]
```

**JSON Payload:**

```json
{
  "image_base64": "base64_encoded_image_data"
}
```

**Response:**

```json
{
  "success": true,
  "barcode": "1234567890123",
  "product_info": {
    "name": "Product Name",
    "brand": "Brand Name",
    "category": "Category",
    "sustainability_indicators": ["Organic", "Fair Trade"],
    "barcode_type": "UPC",
    "confidence": 0.95
  },
  "detected": true
}
```

## Supported Barcode Types

- UPC (Universal Product Code)
- EAN (European Article Number)
- Code 128
- QR Codes
- Data Matrix
- And more (depends on Pixtral's capabilities)

## Camera Permissions

The barcode scanner requires camera access to function. When using the camera feature:

1. Your browser will request camera permissions
2. Grant permission to enable barcode scanning
3. The scanner will prefer the back camera on mobile devices
4. Position barcodes within the scanning frame for best results

## Troubleshooting

### Common Issues

**1. "Barcode scanner not available" error**

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that the Mistral API key is set correctly
- Run the setup script: `python setup_barcode_scanner.py`

**2. Camera not working**

- Check browser permissions for camera access
- Try refreshing the page and granting permissions again
- Use the "Upload Image" option as an alternative

**3. API key issues**

- Verify your Mistral API key is valid
- Check that the environment variable is set correctly
- Restart the server after setting the API key

**4. Low detection accuracy**

- Ensure good lighting when scanning
- Keep the barcode steady and in focus
- Try different angles or distances
- Use high-quality images for uploads

### Error Codes

- **503**: Barcode scanner not available (missing dependencies or API key)
- **400**: Invalid request (missing image data)
- **500**: Server error (check logs for details)

## Development

### Adding New Features

The barcode scanner is modular and can be extended:

1. **Custom Product Database**: Add integration with product databases
2. **Offline Scanning**: Implement local barcode detection
3. **Batch Scanning**: Support multiple barcodes in one image
4. **Enhanced UI**: Improve scanning interface and feedback

### File Structure

```
backend/
├── barcode_scanner.py          # Core barcode scanning logic
├── simple_server.py           # Server with barcode endpoints
├── setup_barcode_scanner.py   # Setup and validation script
└── requirements.txt           # Python dependencies

frontend/app/components/
├── BarcodeScanner.tsx         # React barcode scanner component
└── IntakeForm.tsx            # Form with integrated scanner
```

### Testing

To test the barcode scanner:

1. Use test images with clear barcodes
2. Test both camera and upload functionality
3. Verify API responses contain expected data
4. Check error handling for invalid inputs

## Security Considerations

- Images are processed by Mistral's API (external service)
- Ensure compliance with your privacy policy
- Consider implementing image size limits
- API keys should be kept secure and not exposed in frontend code

## Performance Tips

- Images are automatically resized for optimal API performance
- Camera captures are compressed to JPEG format
- Consider implementing client-side caching for repeated scans
- Monitor API usage to avoid rate limits
