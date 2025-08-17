"use client";
import React, { useState, useRef, useCallback } from "react";
import {
  FaCamera,
  FaUpload,
  FaBarcode,
  FaTimes,
  FaSpinner,
} from "react-icons/fa";

interface BarcodeResult {
  success: boolean;
  barcode: string | null;
  product_info: {
    name?: string;
    brand?: string;
    category?: string;
    sustainability_indicators?: string[];
    barcode_type?: string;
    confidence?: number;
  } | null;
  product_details: {
    name?: string;
    brand?: string;
    category?: string;
    description?: string;
    ingredients?: string[];
  } | null;
  sustainability: {
    name?: string;
    brand?: string;
    category?: string;
    description?: string;
    ingredients?: string[];
    sustainability_score: {
      overall_score: number;
      environmental_impact: number;
      carbon_footprint: number;
      packaging_score: number;
      recyclability: number;
      ethical_sourcing: number;
      certifications: string[];
      improvement_suggestions: string[];
    };
    eco_rating: string;
    environmental_tips: string[];
    alternatives: Array<{
      name: string;
      reason: string;
    }>;
  } | null;
  detected: boolean;
  error?: string;
}

interface BarcodeScannerProps {
  onBarcodeDetected: (barcode: string, productInfo: any) => void;
  onClose: () => void;
  productType?: string; // "food" or "clothing"
}

export default function BarcodeScanner({
  onBarcodeDetected,
  onClose,
  productType = "food",
}: BarcodeScannerProps) {
  const [isScanning, setIsScanning] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [result, setResult] = useState<BarcodeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const startCamera = useCallback(async () => {
    try {
      setLoading(true);
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment", // Use back camera on mobile
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      });

      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play();
      }
      setIsScanning(true);
    } catch (error) {
      console.error("Error accessing camera:", error);
      alert(
        "Could not access camera. Please ensure camera permissions are granted."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
    setIsScanning(false);
  }, [stream]);

  const captureImage = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current) return;

    setLoading(true);
    const canvas = canvasRef.current;
    const video = videoRef.current;

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to blob
    canvas.toBlob(
      async (blob) => {
        if (!blob) return;

        try {
          await scanImage(blob);
        } finally {
          setLoading(false);
        }
      },
      "image/jpeg",
      0.8
    );
  }, []);

  const handleFileUpload = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;

      setLoading(true);
      try {
        await scanImage(file);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const scanImage = async (imageBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append("image", imageBlob);
      formData.append("product_type", productType);

      const response = await fetch("http://localhost:8000/api/scan-barcode", {
        method: "POST",
        body: formData,
      });

      const result: BarcodeResult = await response.json();
      setResult(result);

      if (result.success && result.barcode) {
        onBarcodeDetected(result.barcode, result.product_info);
      }
    } catch (error) {
      console.error("Error scanning barcode:", error);
      setResult({
        success: false,
        barcode: null,
        product_info: null,
        product_details: null,
        sustainability: null,
        detected: false,
        error: "Failed to scan barcode. Please try again.",
      });
    }
  };

  const reset = () => {
    setResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold flex items-center">
            <FaBarcode className="mr-2 text-blue-600" />
            Barcode Scanner
          </h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 p-1"
            title="Close scanner"
            aria-label="Close scanner"
          >
            <FaTimes />
          </button>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-8">
            <FaSpinner className="animate-spin text-2xl text-blue-600 mr-2" />
            <span>Processing...</span>
          </div>
        )}

        {!isScanning && !result && !loading && (
          <div className="space-y-4">
            <p className="text-gray-600 text-sm mb-4">
              Scan a barcode using your camera or upload an image
            </p>

            <button
              onClick={startCamera}
              className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <FaCamera className="mr-2" />
              Use Camera
            </button>

            <div className="relative">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
                title="Upload barcode image"
                placeholder="Choose an image file"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                className="w-full flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <FaUpload className="mr-2" />
                Upload Image
              </button>
            </div>
          </div>
        )}

        {isScanning && (
          <div className="space-y-4">
            <div className="relative">
              <video
                ref={videoRef}
                className="w-full rounded-lg"
                playsInline
                muted
              />
              <canvas ref={canvasRef} className="hidden" />

              {/* Scanning overlay */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="border-2 border-white rounded-lg w-48 h-32 relative">
                  <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-blue-400"></div>
                  <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-blue-400"></div>
                  <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-blue-400"></div>
                  <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-blue-400"></div>
                </div>
              </div>
            </div>

            <div className="flex space-x-2">
              <button
                onClick={captureImage}
                disabled={loading}
                className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                <FaCamera className="mr-2" />
                Capture
              </button>
              <button
                onClick={stopCamera}
                className="flex-1 px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
            </div>

            <p className="text-sm text-gray-600 text-center">
              Position the barcode within the frame and tap Capture
            </p>
          </div>
        )}

        {result && (
          <div className="space-y-4">
            {result.success && result.detected ? (
              <div className="space-y-4">
                {/* Basic Product Information */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-semibold text-green-800 mb-3">
                    🛒 Product Detected!
                  </h4>

                  {result.barcode && (
                    <div className="mb-3">
                      <span className="text-sm font-medium text-gray-700">
                        Barcode:{" "}
                      </span>
                      <span className="font-mono text-sm bg-gray-100 px-2 py-1 rounded">
                        {result.barcode}
                      </span>
                    </div>
                  )}

                  {(result.product_details || result.product_info) && (
                    <div className="space-y-2 text-sm">
                      {(result.product_details?.name ||
                        result.product_info?.name) && (
                        <div>
                          <span className="font-medium text-gray-700">
                            Product:{" "}
                          </span>
                          <span>
                            {result.product_details?.name ||
                              result.product_info?.name}
                          </span>
                        </div>
                      )}

                      {(result.product_details?.brand ||
                        result.product_info?.brand) && (
                        <div>
                          <span className="font-medium text-gray-700">
                            Brand:{" "}
                          </span>
                          <span>
                            {result.product_details?.brand ||
                              result.product_info?.brand}
                          </span>
                        </div>
                      )}

                      {(result.product_details?.category ||
                        result.product_info?.category) && (
                        <div>
                          <span className="font-medium text-gray-700">
                            Category:{" "}
                          </span>
                          <span>
                            {result.product_details?.category ||
                              result.product_info?.category}
                          </span>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Sustainability Information */}
                {result.sustainability && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="font-semibold text-blue-800 mb-3 flex items-center">
                      🌱 Sustainability Analysis
                      <span
                        className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                          result.sustainability.eco_rating === "Excellent"
                            ? "bg-green-100 text-green-800"
                            : result.sustainability.eco_rating === "Good"
                            ? "bg-blue-100 text-blue-800"
                            : result.sustainability.eco_rating === "Fair"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {result.sustainability.eco_rating}
                      </span>
                    </h4>

                    {/* Sustainability Scores */}
                    <div className="grid grid-cols-2 gap-2 mb-4">
                      <div className="text-center p-2 bg-white rounded">
                        <div className="text-lg font-bold text-green-600">
                          {Math.round(
                            result.sustainability.sustainability_score
                              .overall_score
                          )}
                        </div>
                        <div className="text-xs text-gray-600">
                          Overall Score
                        </div>
                      </div>
                      <div className="text-center p-2 bg-white rounded">
                        <div className="text-lg font-bold text-blue-600">
                          {Math.round(
                            result.sustainability.sustainability_score
                              .environmental_impact
                          )}
                        </div>
                        <div className="text-xs text-gray-600">
                          Environmental
                        </div>
                      </div>
                      <div className="text-center p-2 bg-white rounded">
                        <div className="text-lg font-bold text-orange-600">
                          {Math.round(
                            result.sustainability.sustainability_score
                              .carbon_footprint
                          )}
                        </div>
                        <div className="text-xs text-gray-600">Carbon</div>
                      </div>
                      <div className="text-center p-2 bg-white rounded">
                        <div className="text-lg font-bold text-purple-600">
                          {Math.round(
                            result.sustainability.sustainability_score
                              .recyclability
                          )}
                        </div>
                        <div className="text-xs text-gray-600">Recyclable</div>
                      </div>
                    </div>

                    {/* Certifications */}
                    {result.sustainability.sustainability_score.certifications
                      ?.length > 0 && (
                      <div className="mb-3">
                        <span className="font-medium text-blue-700 text-sm">
                          Certifications:{" "}
                        </span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {result.sustainability.sustainability_score.certifications.map(
                            (cert, index) => (
                              <span
                                key={index}
                                className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs"
                              >
                                {cert}
                              </span>
                            )
                          )}
                        </div>
                      </div>
                    )}

                    {/* Environmental Tips */}
                    {result.sustainability.environmental_tips?.length > 0 && (
                      <div className="mb-3">
                        <span className="font-medium text-blue-700 text-sm block mb-2">
                          💡 Environmental Tips:
                        </span>
                        <ul className="text-xs text-blue-700 space-y-1">
                          {result.sustainability.environmental_tips
                            .slice(0, 2)
                            .map((tip, index) => (
                              <li key={index} className="flex items-start">
                                <span className="mr-1">•</span>
                                <span>{tip}</span>
                              </li>
                            ))}
                        </ul>
                      </div>
                    )}

                    {/* Sustainable Alternatives */}
                    {result.sustainability.alternatives?.length > 0 && (
                      <div>
                        <span className="font-medium text-blue-700 text-sm block mb-2">
                          🔄 Better Alternatives:
                        </span>
                        <div className="space-y-1">
                          {result.sustainability.alternatives
                            .slice(0, 2)
                            .map((alt, index) => (
                              <div
                                key={index}
                                className="text-xs bg-white p-2 rounded"
                              >
                                <div className="font-medium text-blue-800">
                                  {alt.name}
                                </div>
                                <div className="text-blue-600">
                                  {alt.reason}
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Legacy compatibility for basic product info */}
                {!result.sustainability && result.product_info && (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <h4 className="font-semibold text-gray-800 mb-2">
                      Basic Product Info
                    </h4>

                    {result.product_info.sustainability_indicators &&
                      result.product_info.sustainability_indicators.length >
                        0 && (
                        <div>
                          <span className="font-medium text-gray-700 text-sm">
                            Eco Labels:{" "}
                          </span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {result.product_info.sustainability_indicators.map(
                              (indicator, index) => (
                                <span
                                  key={index}
                                  className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs"
                                >
                                  {indicator}
                                </span>
                              )
                            )}
                          </div>
                        </div>
                      )}

                    {result.product_info.confidence && (
                      <div className="mt-2">
                        <span className="font-medium text-gray-700 text-sm">
                          Confidence:{" "}
                        </span>
                        <span className="text-sm">
                          {Math.round(result.product_info.confidence * 100)}%
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h4 className="font-semibold text-yellow-800 mb-2">
                  No Barcode Detected
                </h4>
                <p className="text-sm text-yellow-700">
                  {result.error ||
                    "Could not detect a barcode in this image. Please try again with a clearer image."}
                </p>
              </div>
            )}

            <div className="flex space-x-2">
              <button
                onClick={reset}
                className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Scan Another
              </button>
              <button
                onClick={onClose}
                className="flex-1 px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
