"use client";
import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";
import {
  FaLeaf,
  FaUtensils,
  FaTshirt,
  FaBicycle,
  FaCar,
  FaCheckCircle,
  FaArrowRight,
  FaArrowLeft,
  FaRegSmile,
  FaBarcode,
} from "react-icons/fa";
import { useRouter } from "next/navigation";
import BarcodeScanner from "./BarcodeScanner";

type FormValues = {
  meal_type: string;
  food_barcode?: string;
  meal_origin: string;
  meal_leftovers: string;
  outfit_material: string;
  clothing_barcode?: string;
  outfit_image?: FileList;
  mobility_mode: string;
  mobility_distance: string;
  resource_action: string[];
  climate_commitment: string;
  reflection: string;
  feedback: string;
};

const MEAL_OPTIONS = [
  {
    value: "plant-based",
    label: "Plant-based",
    icon: <FaLeaf className="inline mr-1 text-green-600" />,
  },
  {
    value: "mixed",
    label: "Mixed (plant & animal)",
    icon: <FaUtensils className="inline mr-1 text-yellow-600" />,
  },
  {
    value: "meat-heavy",
    label: "Meat-heavy",
    icon: <FaUtensils className="inline mr-1 text-red-600" />,
  },
  {
    value: "snack",
    label: "Snack",
    icon: <FaUtensils className="inline mr-1 text-blue-600" />,
  },
  {
    value: "drink",
    label: "Drink",
    icon: <FaUtensils className="inline mr-1 text-purple-600" />,
  },
];
const MEAL_ORIGIN_OPTIONS = [
  "Locally sourced",
  "Supermarket",
  "Takeaway/Restaurant",
  "Home-grown",
  "Don't know",
];
const MEAL_LEFTOVERS_OPTIONS = [
  "None left",
  "Some left (will eat later)",
  "Some left (will throw away)",
  "Didn't finish, not sure what happened",
];
const OUTFIT_OPTIONS = [
  {
    value: "mostly synthetic",
    label: "Mostly synthetic",
    icon: <FaTshirt className="inline mr-1 text-blue-500" />,
  },
  {
    value: "mostly natural",
    label: "Mostly natural",
    icon: <FaTshirt className="inline mr-1 text-green-700" />,
  },
  {
    value: "mixed",
    label: "Mixed",
    icon: <FaTshirt className="inline mr-1 text-yellow-700" />,
  },
];
const MOBILITY_OPTIONS = [
  {
    value: "walk",
    label: "Walk",
    icon: <FaBicycle className="inline mr-1 text-green-600" />,
  },
  {
    value: "bike",
    label: "Bike",
    icon: <FaBicycle className="inline mr-1 text-blue-600" />,
  },
  {
    value: "bus",
    label: "Bus",
    icon: <FaCar className="inline mr-1 text-yellow-600" />,
  },
  {
    value: "car",
    label: "Car",
    icon: <FaCar className="inline mr-1 text-red-600" />,
  },
  {
    value: "train",
    label: "Train",
    icon: <FaCar className="inline mr-1 text-purple-600" />,
  },
  {
    value: "other",
    label: "Other",
    icon: <FaCar className="inline mr-1 text-gray-600" />,
  },
];
const RESOURCE_OPTIONS = [
  "Used a reusable bottle/cup",
  "Turned off lights/electronics",
  "Recycled something",
  "Chose a plant-based meal",
  "Used public/shared transport",
  "None of these",
];
const CLIMATE_COMMITMENT_OPTIONS = [
  "Try a new plant-based meal",
  "Walk or bike more often",
  "Buy second-hand clothes",
  "Reduce food waste",
  "Talk to a friend about climate",
  "Other",
];

export default function IntakeForm() {
  const { register, handleSubmit, watch, reset, setValue, getValues } =
    useForm<FormValues>({
      defaultValues: {
        meal_type: "plant-based",
        meal_origin: "Locally sourced",
        meal_leftovers: "None left",
        outfit_material: "mostly synthetic",
        mobility_mode: "walk",
        mobility_distance: "1",
        resource_action: [],
        climate_commitment: "Try a new plant-based meal",
        reflection: "",
        feedback: "3",
        food_barcode: "",
        clothing_barcode: "",
      },
    });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(0);
  const [showBarcodeScanner, setShowBarcodeScanner] = useState(false);
  const [showClothingBarcodeScanner, setShowClothingBarcodeScanner] = useState(false);
  const [productInfo, setProductInfo] = useState<any>(null);
  const [clothingProductInfo, setClothingProductInfo] = useState<any>(null);
  const [searchingProduct, setSearchingProduct] = useState(false);
  const [searchingClothingProduct, setSearchingClothingProduct] = useState(false);
  const [lastSearchedBarcode, setLastSearchedBarcode] = useState("");
  const [lastSearchedClothingBarcode, setLastSearchedClothingBarcode] = useState("");
  
  // Category confirmation states
  const [showFoodCategoryConfirmation, setShowFoodCategoryConfirmation] = useState(false);
  const [showClothingCategoryConfirmation, setShowClothingCategoryConfirmation] = useState(false);
  const [pendingFoodProduct, setPendingFoodProduct] = useState<any>(null);
  const [pendingClothingProduct, setPendingClothingProduct] = useState<any>(null);
  const router = useRouter();

  // Watch for barcode changes to trigger automatic search
  const currentBarcode = watch("food_barcode");
  const currentClothingBarcode = watch("clothing_barcode");

  // Auto-search when food barcode changes
  useEffect(() => {
    const trimmedBarcode = currentBarcode?.trim() || "";

    // Only search if:
    // 1. Barcode is not empty
    // 2. Barcode is different from last searched
    // 3. Barcode has a reasonable length (typically 8-14 digits)
    // 4. Not currently searching
    if (
      trimmedBarcode &&
      trimmedBarcode !== lastSearchedBarcode &&
      trimmedBarcode.length >= 8 &&
      /^\d+$/.test(trimmedBarcode) &&
      !searchingProduct
    ) {
      // Debounce the search to avoid too many API calls
      const searchTimeout = setTimeout(() => {
        console.log(`🔍 Auto-searching for food barcode: ${trimmedBarcode}`);
        searchProduct(trimmedBarcode);
      }, 1000); // Wait 1 second after user stops typing

      return () => clearTimeout(searchTimeout);
    }
  }, [currentBarcode, lastSearchedBarcode, searchingProduct]);

  // Auto-search when clothing barcode changes
  useEffect(() => {
    const trimmedBarcode = currentClothingBarcode?.trim() || "";

    // Only search if:
    // 1. Barcode is not empty
    // 2. Barcode is different from last searched
    // 3. Barcode has a reasonable length (typically 8-14 digits)
    // 4. Not currently searching
    if (
      trimmedBarcode &&
      trimmedBarcode !== lastSearchedClothingBarcode &&
      trimmedBarcode.length >= 8 &&
      /^\d+$/.test(trimmedBarcode) &&
      !searchingClothingProduct
    ) {
      // Debounce the search to avoid too many API calls
      const searchTimeout = setTimeout(() => {
        console.log(`🔍 Auto-searching for clothing barcode: ${trimmedBarcode}`);
        searchClothingProduct(trimmedBarcode);
      }, 1000); // Wait 1 second after user stops typing

      return () => clearTimeout(searchTimeout);
    }
  }, [currentClothingBarcode, lastSearchedClothingBarcode, searchingClothingProduct]);

  // Function to determine meal type from product category
  const determineMealType = (productInfo: any): string => {
    if (!productInfo) return "";

    const category = productInfo.category?.toLowerCase() || "";
    const name = productInfo.name?.toLowerCase() || "";

    console.log(
      `🍽️ Determining meal type for category: "${category}", name: "${name}"`
    );

    // Check for drinks first
    if (
      category.includes("drink") ||
      category.includes("beverage") ||
      category.includes("juice") ||
      category.includes("soda") ||
      name.includes("juice") ||
      name.includes("water") ||
      name.includes("cola") ||
      name.includes("drink")
    ) {
      return "drink";
    }

    // Check for snacks
    if (
      category.includes("snack") ||
      category.includes("chip") ||
      category.includes("cookie") ||
      category.includes("candy") ||
      category.includes("chocolate") ||
      category.includes("biscuit") ||
      name.includes("crisp") ||
      name.includes("chip") ||
      name.includes("cookie") ||
      name.includes("candy")
    ) {
      return "snack";
    }

    // Check for meat-heavy meals
    if (
      category.includes("meat") ||
      category.includes("beef") ||
      category.includes("pork") ||
      category.includes("chicken") ||
      category.includes("fish") ||
      name.includes("meat") ||
      name.includes("beef") ||
      name.includes("chicken")
    ) {
      return "meat-heavy";
    }

    // Check for plant-based meals
    if (
      category.includes("vegetarian") ||
      category.includes("vegan") ||
      category.includes("plant") ||
      category.includes("organic") ||
      name.includes("organic") ||
      name.includes("plant")
    ) {
      return "plant-based";
    }

    // Default to mixed for other food items
    return "mixed";
  };

  const determineOutfitMaterial = (productInfo: any): string => {
    if (!productInfo) return "";

    const category = productInfo.category?.toLowerCase() || "";
    const name = productInfo.name?.toLowerCase() || "";
    const materials = productInfo.materials || [];

    console.log(
      `👕 Determining outfit material for category: "${category}", name: "${name}", materials: [${materials.join(", ")}]`
    );

    // Count synthetic vs natural materials
    let syntheticCount = 0;
    let naturalCount = 0;

    materials.forEach((material: string) => {
      const mat = material.toLowerCase();
      if (
        mat.includes("polyester") ||
        mat.includes("nylon") ||
        mat.includes("acrylic") ||
        mat.includes("synthetic") ||
        mat.includes("plastic") ||
        mat.includes("spandex") ||
        mat.includes("elastane")
      ) {
        syntheticCount++;
      } else if (
        mat.includes("cotton") ||
        mat.includes("wool") ||
        mat.includes("silk") ||
        mat.includes("linen") ||
        mat.includes("hemp") ||
        mat.includes("organic") ||
        mat.includes("natural")
      ) {
        naturalCount++;
      }
    });

    // Also check in product name and category
    if (
      name.includes("polyester") ||
      name.includes("synthetic") ||
      category.includes("synthetic")
    ) {
      syntheticCount++;
    }

    if (
      name.includes("cotton") ||
      name.includes("organic") ||
      name.includes("natural") ||
      category.includes("organic") ||
      category.includes("natural")
    ) {
      naturalCount++;
    }

    // Determine material type based on counts
    if (naturalCount > syntheticCount) {
      return "mostly natural";
    } else if (syntheticCount > naturalCount) {
      return "mostly synthetic";
    } else {
      return "mixed";
    }
  };

  const steps = [
    "Meal Choices",
    "Meal Details",
    "Outfit",
    "Mobility",
    "Actions",
    "Commitment",
    "Reflection",
    "Feedback",
  ];

  const handleBarcodeDetected = (barcode: string, productInfo: any) => {
    setValue("food_barcode", barcode);
    setShowBarcodeScanner(false);

    if (productInfo) {
      // Check if category confirmation is needed for camera-detected products
      if (productInfo.category_mismatch || (productInfo.category_confidence && productInfo.category_confidence < 0.7)) {
        console.log(`⚠️ Category confirmation needed for camera scan - Expected: food, Detected: ${productInfo.detected_category}, Confidence: ${productInfo.category_confidence}`);
        setPendingFoodProduct(productInfo);
        setShowFoodCategoryConfirmation(true);
      } else {
        // Category is confirmed, proceed normally
        setProductInfo(productInfo);
        const mealType = determineMealType(productInfo);
        if (mealType) {
          setValue("meal_type", mealType);
          console.log(`🍽️ Auto-selected meal type from scan: ${mealType}`);
        }
      }
    }

    console.log("📷 Barcode detected from camera:", barcode, productInfo);
  };

  const searchProduct = async (barcode: string) => {
    if (!barcode || barcode.trim() === "") {
      alert("Please enter a barcode number");
      return;
    }

    const trimmedBarcode = barcode.trim();
    setSearchingProduct(true);
    setProductInfo(null);
    setLastSearchedBarcode(trimmedBarcode);

    try {
      console.log(`🔍 Searching for product with barcode: ${trimmedBarcode}`);

      const response = await fetch(
        "http://localhost:8000/api/product-sustainability",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ 
            barcode: trimmedBarcode,
            product_type: "food"
          }),
        }
      );

      const result = await response.json();

      if (result.success && result.sustainability) {
        console.log("✅ Product found:", result.sustainability);

        // Check if category confirmation is needed
        if (result.sustainability.category_mismatch || result.sustainability.category_confidence < 0.7) {
          console.log(`⚠️ Category confirmation needed - Expected: food, Detected: ${result.sustainability.detected_category}, Confidence: ${result.sustainability.category_confidence}`);
          setPendingFoodProduct(result.sustainability);
          setShowFoodCategoryConfirmation(true);
        } else {
          // Category is confirmed, proceed normally
          setProductInfo(result.sustainability);
          const mealType = determineMealType(result.sustainability);
          if (mealType) {
            setValue("meal_type", mealType);
            console.log(`🍽️ Auto-selected meal type: ${mealType}`);
          }
        }
      } else {
        console.log("❌ Product not found:", result.error);
        alert(
          result.error ||
            "Product not found. Please check the barcode and try again."
        );
      }
    } catch (error) {
      console.error("❌ Error searching for product:", error);
      alert(
        "Failed to search for product. Please make sure the backend server is running."
      );
    } finally {
      setSearchingProduct(false);
    }
  };

  const searchClothingProduct = async (barcode: string) => {
    if (!barcode || barcode.trim() === "") {
      alert("Please enter a clothing barcode number");
      return;
    }

    const trimmedBarcode = barcode.trim();
    setSearchingClothingProduct(true);
    setClothingProductInfo(null);
    setLastSearchedClothingBarcode(trimmedBarcode);

    try {
      console.log(`🔍 Searching for clothing product with barcode: ${trimmedBarcode}`);

      const response = await fetch(
        "http://localhost:8000/api/product-sustainability",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ 
            barcode: trimmedBarcode,
            product_type: "clothing"
          }),
        }
      );

      const result = await response.json();

      if (result.success && result.sustainability) {
        console.log("✅ Clothing product found:", result.sustainability);

        // Check if category confirmation is needed
        if (result.sustainability.category_mismatch || result.sustainability.category_confidence < 0.7) {
          console.log(`⚠️ Category confirmation needed - Expected: clothing, Detected: ${result.sustainability.detected_category}, Confidence: ${result.sustainability.category_confidence}`);
          setPendingClothingProduct(result.sustainability);
          setShowClothingCategoryConfirmation(true);
        } else {
          // Category is confirmed, proceed normally
          setClothingProductInfo(result.sustainability);
          const outfitMaterial = determineOutfitMaterial(result.sustainability);
          if (outfitMaterial) {
            setValue("outfit_material", outfitMaterial);
            console.log(`👕 Auto-selected outfit material: ${outfitMaterial}`);
          }
        }
      } else {
        console.log("❌ Clothing product not found:", result.error);
        alert(
          result.error ||
            "Clothing product not found. Please check the barcode and try again."
        );
      }
    } catch (error) {
      console.error("❌ Error searching for clothing product:", error);
      alert(
        "Failed to search for clothing product. Please make sure the backend server is running."
      );
    } finally {
      setSearchingClothingProduct(false);
    }
  };

  const handleSearchButtonClick = () => {
    const barcode = watch("food_barcode");
    if (barcode) {
      searchProduct(barcode);
    }
  };

  const handleClothingSearchButtonClick = () => {
    const barcode = watch("clothing_barcode");
    if (barcode) {
      searchClothingProduct(barcode);
    }
  };

  // Category confirmation handlers
  const handleFoodCategoryConfirm = (isCorrect: boolean) => {
    if (isCorrect && pendingFoodProduct) {
      // User confirms it's a food product
      setProductInfo(pendingFoodProduct);
      const mealType = determineMealType(pendingFoodProduct);
      if (mealType) {
        setValue("meal_type", mealType);
        console.log(`🍽️ Auto-selected meal type after confirmation: ${mealType}`);
      }
    } else {
      // User says it's not a food product - clear the barcode
      setValue("food_barcode", "");
      setProductInfo(null);
      alert("Please scan or enter a food product barcode.");
    }
    setShowFoodCategoryConfirmation(false);
    setPendingFoodProduct(null);
  };

  const handleClothingCategoryConfirm = (isCorrect: boolean) => {
    if (isCorrect && pendingClothingProduct) {
      // User confirms it's a clothing product
      setClothingProductInfo(pendingClothingProduct);
      const outfitMaterial = determineOutfitMaterial(pendingClothingProduct);
      if (outfitMaterial) {
        setValue("outfit_material", outfitMaterial);
        console.log(`👕 Auto-selected outfit material after confirmation: ${outfitMaterial}`);
      }
    } else {
      // User says it's not a clothing product - clear the barcode
      setValue("clothing_barcode", "");
      setClothingProductInfo(null);
      alert("Please scan or enter a clothing product barcode.");
    }
    setShowClothingCategoryConfirmation(false);
    setPendingClothingProduct(null);
  };

  const onSubmit = async (data: FormValues) => {
    setLoading(true);
    const formData = new FormData();
    formData.append("item_type", "meal");
    const responses: any = {
      meal_type: data.meal_type,
      meal_origin: data.meal_origin,
      meal_leftovers: data.meal_leftovers,
      outfit_material: data.outfit_material,
      food_barcode: data.food_barcode,
      clothing_barcode: data.clothing_barcode,
      mobility_mode: data.mobility_mode,
      mobility_distance: data.mobility_distance,
      resource_action: data.resource_action,
      climate_commitment: data.climate_commitment,
      reflection: data.reflection,
      feedback: data.feedback,
    };
    formData.append("form_responses", JSON.stringify(responses));
    if (data.outfit_image && data.outfit_image.length > 0) {
      formData.append("image", data.outfit_image[0]);
    }
    if (data.food_barcode) {
      formData.append("food_barcode", data.food_barcode);
    }
    if (data.clothing_barcode) {
      formData.append("clothing_barcode", data.clothing_barcode);
    }
    try {
      // Submit the form data
      const res = await axios.post(
        "http://localhost:8000/api/intake",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      // Navigate to the results page with the result data
      router.push(
        `/results?result=${encodeURIComponent(JSON.stringify(res.data))}`
      );
      setLoading(false);
    } catch (e) {
      setResult({ error: "Submission failed" });
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto bg-white shadow-xl rounded-2xl p-8 mt-8 animate-fade-in">
      <div className="flex items-center mb-6">
        <FaLeaf className="text-green-600 text-3xl mr-2" />
        <h2 className="text-2xl font-bold tracking-tight">
          EcoBee Intake & Perception
        </h2>
      </div>
      <div className="flex items-center mb-8">
        {steps.map((label, idx) => (
          <React.Fragment key={label}>
            <div
              className={`flex flex-col items-center ${
                idx === step ? "text-blue-600" : "text-gray-400"
              }`}
            >
              <div
                className={`rounded-full border-2 ${
                  idx === step
                    ? "border-blue-600 bg-blue-100"
                    : "border-gray-300 bg-white"
                } w-8 h-8 flex items-center justify-center font-bold`}
              >
                {idx + 1}
              </div>
              <span className="text-xs mt-1 text-center w-16">{label}</span>
            </div>
            {idx < steps.length - 1 && (
              <div className="flex-1 h-1 bg-gray-200 mx-1" />
            )}
          </React.Fragment>
        ))}
      </div>
      <form onSubmit={handleSubmit(onSubmit)}>
        {/* Step 1: Meal Choices */}
        {step === 0 && (
          <div className="space-y-6 animate-fade-in">
            <label className="block">
              <span className="font-medium text-lg flex items-center">
                <FaBarcode className="mr-2 text-blue-700" />
                Food product barcode{" "}
                <span className="ml-2 text-xs text-gray-400">(optional)</span>
                {searchingProduct && (
                  <span className="ml-2 flex items-center text-sm text-blue-600">
                    <div className="animate-spin rounded-full h-3 w-3 border-2 border-blue-600 border-t-transparent mr-1"></div>
                    Searching...
                  </span>
                )}
              </span>
              <div className="mt-2 space-y-3">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    {...register("food_barcode")}
                    className="flex-1 block w-full rounded border-gray-300"
                    placeholder="Enter barcode number (e.g., 5012035927608)"
                  />
                  <button
                    type="button"
                    onClick={handleSearchButtonClick}
                    disabled={searchingProduct}
                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors flex items-center disabled:bg-gray-400"
                    title="Search Product"
                  >
                    {searchingProduct ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                        Searching...
                      </>
                    ) : (
                      <>
                        <FaLeaf className="mr-2" />
                        Search Product
                      </>
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowBarcodeScanner(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors flex items-center"
                    title="Scan Barcode"
                  >
                    <FaBarcode className="mr-2" />
                    Scan
                  </button>
                </div>
                <p className="text-sm text-gray-600">
                  💡 Enter a barcode number - it will automatically search for
                  product info and select the meal type! You can also click
                  "Search Product" manually or use "Scan" for camera scanning.
                </p>
              </div>
            </label>

            {/* Product Sustainability Information Display */}
            {productInfo && (
              <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-6 mt-4">
                <h4 className="font-bold text-green-800 mb-4 flex items-center text-lg">
                  🛒 Product Found!
                  <span
                    className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                      productInfo.eco_rating === "Excellent"
                        ? "bg-green-100 text-green-800"
                        : productInfo.eco_rating === "Good"
                        ? "bg-blue-100 text-blue-800"
                        : productInfo.eco_rating === "Fair"
                        ? "bg-yellow-100 text-yellow-800"
                        : "bg-red-100 text-red-800"
                    }`}
                  >
                    {productInfo.eco_rating}
                  </span>
                </h4>

                {/* Basic Product Information */}
                <div className="mb-4 space-y-2">
                  {productInfo.name && (
                    <div className="flex">
                      <span className="font-medium text-gray-700 w-24">
                        Product:
                      </span>
                      <span className="text-gray-900">{productInfo.name}</span>
                    </div>
                  )}
                  {productInfo.brand && (
                    <div className="flex">
                      <span className="font-medium text-gray-700 w-24">
                        Brand:
                      </span>
                      <span className="text-gray-900">{productInfo.brand}</span>
                    </div>
                  )}
                  {productInfo.category && (
                    <div className="flex">
                      <span className="font-medium text-gray-700 w-24">
                        Category:
                      </span>
                      <span className="text-gray-900">
                        {productInfo.category}
                      </span>
                    </div>
                  )}
                </div>

                {/* Sustainability Scores */}
                {productInfo.sustainability_score && (
                  <div className="mb-4">
                    <h5 className="font-semibold text-green-800 mb-3">
                      🌱 Sustainability Scores
                    </h5>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="text-center p-3 bg-white rounded shadow-sm">
                        <div className="text-2xl font-bold text-green-600">
                          {Math.round(
                            productInfo.sustainability_score.overall_score
                          )}
                        </div>
                        <div className="text-xs text-gray-600">
                          Overall Score
                        </div>
                      </div>
                      <div className="text-center p-3 bg-white rounded shadow-sm">
                        <div className="text-2xl font-bold text-blue-600">
                          {Math.round(
                            productInfo.sustainability_score
                              .environmental_impact
                          )}
                        </div>
                        <div className="text-xs text-gray-600">
                          Environmental Impact
                        </div>
                      </div>
                      <div className="text-center p-3 bg-white rounded shadow-sm">
                        <div className="text-2xl font-bold text-orange-600">
                          {Math.round(
                            productInfo.sustainability_score.carbon_footprint
                          )}
                        </div>
                        <div className="text-xs text-gray-600">
                          Carbon Footprint
                        </div>
                      </div>
                      <div className="text-center p-3 bg-white rounded shadow-sm">
                        <div className="text-2xl font-bold text-purple-600">
                          {Math.round(
                            productInfo.sustainability_score.recyclability
                          )}
                        </div>
                        <div className="text-xs text-gray-600">
                          Recyclability
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Certifications */}
                {productInfo.sustainability_score?.certifications?.length >
                  0 && (
                  <div className="mb-4">
                    <h5 className="font-semibold text-green-800 mb-2">
                      🏆 Certifications
                    </h5>
                    <div className="flex flex-wrap gap-2">
                      {productInfo.sustainability_score.certifications.map(
                        (cert: string, index: number) => (
                          <span
                            key={index}
                            className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm"
                          >
                            {cert}
                          </span>
                        )
                      )}
                    </div>
                  </div>
                )}

                {/* Environmental Tips */}
                {productInfo.environmental_tips?.length > 0 && (
                  <div className="mb-4">
                    <h5 className="font-semibold text-blue-800 mb-2">
                      💡 Environmental Tips
                    </h5>
                    <ul className="text-sm text-blue-700 space-y-1">
                      {productInfo.environmental_tips
                        .slice(0, 3)
                        .map((tip: string, index: number) => (
                          <li key={index} className="flex items-start">
                            <span className="mr-2 text-blue-500">•</span>
                            <span>{tip}</span>
                          </li>
                        ))}
                    </ul>
                  </div>
                )}

                {/* Improvement Suggestions */}
                {productInfo.sustainability_score?.improvement_suggestions
                  ?.length > 0 && (
                  <div className="mb-4">
                    <h5 className="font-semibold text-orange-800 mb-2">
                      🎯 Improvement Suggestions
                    </h5>
                    <ul className="text-sm text-orange-700 space-y-1">
                      {productInfo.sustainability_score.improvement_suggestions
                        .slice(0, 3)
                        .map((suggestion: string, index: number) => (
                          <li key={index} className="flex items-start">
                            <span className="mr-2 text-orange-500">•</span>
                            <span>{suggestion}</span>
                          </li>
                        ))}
                    </ul>
                  </div>
                )}

                {/* Sustainable Alternatives */}
                {productInfo.alternatives?.length > 0 && (
                  <div>
                    <h5 className="font-semibold text-purple-800 mb-2">
                      🔄 Better Alternatives
                    </h5>
                    <div className="space-y-2">
                      {productInfo.alternatives
                        .slice(0, 2)
                        .map((alt: any, index: number) => (
                          <div
                            key={index}
                            className="bg-white p-3 rounded shadow-sm"
                          >
                            <div className="font-medium text-purple-800">
                              {alt.name}
                            </div>
                            <div className="text-sm text-purple-600">
                              {alt.reason}
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Meal type selection with auto-selection indicator */}
            <label className="block">
              <span className="font-medium text-lg flex items-center">
                What type of meal/item was this?
                {productInfo && (
                  <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                    ✨ Auto-detected
                  </span>
                )}
              </span>
              <div className="grid grid-cols-1 gap-2 mt-2">
                {MEAL_OPTIONS.map((opt) => (
                  <label
                    key={opt.value}
                    className="flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="radio"
                      value={opt.value}
                      {...register("meal_type")}
                      className="mr-2"
                    />
                    {opt.icon} {opt.label}
                  </label>
                ))}
              </div>
            </label>
          </div>
        )}
        {/* Step 2: Meal Details */}
        {step === 1 && (
          <div className="space-y-6 animate-fade-in">
            <label className="block">
              <span className="font-medium text-lg">
                Where did your meal come from?
              </span>
              <select
                {...register("meal_origin")}
                className="mt-2 block w-full rounded border-gray-300"
              >
                {MEAL_ORIGIN_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="font-medium text-lg">
                Did you have any leftovers?
              </span>
              <select
                {...register("meal_leftovers")}
                className="mt-2 block w-full rounded border-gray-300"
              >
                {MEAL_LEFTOVERS_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </label>
          </div>
        )}
        {/* Step 3: Outfit */}
        {step === 2 && (
          <div className="space-y-6 animate-fade-in">
            <label className="block">
              <span className="font-medium text-lg flex items-center">
                <FaTshirt className="mr-2 text-blue-700" />
                What are you wearing today?
              </span>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {OUTFIT_OPTIONS.map((opt) => (
                  <label
                    key={opt.value}
                    className={`flex items-center p-2 rounded-lg border cursor-pointer transition-all ${
                      watch("outfit_material") === opt.value
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 bg-white hover:bg-gray-50"
                    }`}
                  >
                    <input
                      type="radio"
                      value={opt.value}
                      {...register("outfit_material")}
                      className="mr-2"
                    />
                    {opt.icon} {opt.label}
                  </label>
                ))}
              </div>
            </label>

            {/* Clothing Barcode Input */}
            <label className="block">
              <span className="font-medium text-lg flex items-center">
                <FaBarcode className="mr-2 text-purple-700" />
                Scan clothing tag barcode
                <span className="ml-2 text-xs text-gray-400">(optional)</span>
              </span>
              <div className="flex gap-2 mt-2">
                <input
                  type="text"
                  {...register("clothing_barcode")}
                  placeholder="Enter clothing barcode..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  type="button"
                  onClick={() => setShowClothingBarcodeScanner(true)}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  📷 Scan
                </button>
                <button
                  type="button"
                  onClick={handleClothingSearchButtonClick}
                  disabled={searchingClothingProduct}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {searchingClothingProduct ? "🔍..." : "🔍 Search"}
                </button>
              </div>
            </label>

            {/* Clothing Product Information Display */}
            {clothingProductInfo && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-bold text-green-800 mb-2">
                  ✅ Clothing Product Found!
                </h4>
                <div className="text-sm text-green-700">
                  <p><strong>Product:</strong> {clothingProductInfo.name}</p>
                  {clothingProductInfo.brand && (
                    <p><strong>Brand:</strong> {clothingProductInfo.brand}</p>
                  )}
                  {clothingProductInfo.materials && clothingProductInfo.materials.length > 0 && (
                    <p><strong>Materials:</strong> {clothingProductInfo.materials.join(", ")}</p>
                  )}
                  <p><strong>Sustainability Score:</strong> {clothingProductInfo.overall_score}/100</p>
                </div>
              </div>
            )}

            {/* Clothing Barcode Scanner Modal */}
            {showClothingBarcodeScanner && (
              <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
                <div className="bg-white rounded-lg p-4 max-w-md w-full m-4">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold">Scan Clothing Barcode</h3>
                    <button
                      onClick={() => setShowClothingBarcodeScanner(false)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      ✕
                    </button>
                  </div>
                  <BarcodeScanner
                    onBarcodeDetected={(barcode: string, productInfo: any) => {
                      setValue("clothing_barcode", barcode);
                      setShowClothingBarcodeScanner(false);
                      if (productInfo) {
                        setClothingProductInfo(productInfo);
                        const outfitMaterial = determineOutfitMaterial(productInfo);
                        if (outfitMaterial) {
                          setValue("outfit_material", outfitMaterial);
                          console.log(`👕 Auto-selected outfit material from scan: ${outfitMaterial}`);
                        }
                      }
                      console.log("📷 Clothing barcode detected from camera:", barcode, productInfo);
                    }}
                    onClose={() => setShowClothingBarcodeScanner(false)}
                    productType="clothing"
                  />
                </div>
              </div>
            )}

            <label className="block">
              <span className="font-medium text-lg">
                Upload a photo of your outfit{" "}
                <span className="ml-2 text-xs text-gray-400">(optional)</span>
              </span>
              <input
                type="file"
                {...register("outfit_image")}
                accept="image/*"
                className="mt-2"
              />
            </label>
          </div>
        )}
        {/* Step 4: Mobility */}
        {step === 3 && (
          <div className="space-y-6 animate-fade-in">
            <label className="block">
              <span className="font-medium text-lg flex items-center">
                <FaBicycle className="mr-2 text-green-700" />
                How did you travel to campus today?
              </span>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {MOBILITY_OPTIONS.map((opt) => (
                  <label
                    key={opt.value}
                    className={`flex items-center p-2 rounded-lg border cursor-pointer transition-all ${
                      watch("mobility_mode") === opt.value
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 bg-white hover:bg-gray-50"
                    }`}
                  >
                    <input
                      type="radio"
                      value={opt.value}
                      {...register("mobility_mode")}
                      className="mr-2"
                    />
                    {opt.icon} {opt.label}
                  </label>
                ))}
              </div>
            </label>
            <label className="block">
              <span className="font-medium text-lg">
                Roughly how far did you travel today? (km)
              </span>
              <input
                type="number"
                min="0"
                max="100"
                step="1"
                {...register("mobility_distance")}
                className="mt-2 block w-full rounded border-gray-300"
              />
            </label>
          </div>
        )}
        {/* Step 5: Actions */}
        {step === 4 && (
          <div className="space-y-6 animate-fade-in">
            <label className="block">
              <span className="font-medium text-lg">
                Which of these sustainable actions did you take today?
              </span>
              <div className="grid grid-cols-1 gap-2 mt-2">
                {RESOURCE_OPTIONS.map((opt) => (
                  <label
                    key={opt}
                    className={`flex items-center p-2 rounded-lg border cursor-pointer transition-all ${
                      watch("resource_action")?.includes(opt)
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 bg-white hover:bg-gray-50"
                    }`}
                  >
                    <input
                      type="checkbox"
                      value={opt}
                      {...register("resource_action")}
                      className="mr-2"
                    />
                    {opt}
                  </label>
                ))}
              </div>
            </label>
          </div>
        )}
        {/* Step 6: Commitment */}
        {step === 5 && (
          <div className="space-y-6 animate-fade-in">
            <label className="block">
              <span className="font-medium text-lg">
                Which sustainable action will you try next?
              </span>
              <select
                {...register("climate_commitment")}
                className="mt-2 block w-full rounded border-gray-300"
              >
                {CLIMATE_COMMITMENT_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </label>
          </div>
        )}
        {/* Step 7: Reflection */}
        {step === 6 && (
          <div className="space-y-6 animate-fade-in">
            <label className="block">
              <span className="font-medium text-lg">
                In one sentence, what does sustainability mean to you?
              </span>
              <input
                type="text"
                {...register("reflection")}
                className="mt-2 block w-full rounded border-gray-300"
                placeholder="Your answer"
              />
            </label>
          </div>
        )}
        {/* Step 8: Feedback */}
        {step === 7 && (
          <div className="space-y-6 animate-fade-in">
            <label className="block">
              <span className="font-medium text-lg flex items-center">
                <FaRegSmile className="mr-2 text-yellow-500" />
                How useful was this quiz for your climate awareness?
              </span>
              <div className="flex gap-2 mt-2">
                {[1, 2, 3, 4, 5].map((n) => (
                  <label
                    key={n}
                    className={`flex flex-col items-center p-2 rounded-lg border cursor-pointer transition-all ${
                      watch("feedback") === String(n)
                        ? "border-blue-500 bg-blue-50"
                        : "border-gray-200 bg-white hover:bg-gray-50"
                    }`}
                  >
                    <input
                      type="radio"
                      value={n}
                      {...register("feedback")}
                      className="mb-1"
                    />
                    <span className="text-lg">{n}</span>
                  </label>
                ))}
              </div>
            </label>
            <div className="mt-8">
              <button
                type="submit"
                className="w-full px-6 py-3 rounded bg-green-600 text-white font-bold flex items-center justify-center hover:bg-green-700 transition-all"
                disabled={loading}
              >
                {loading ? (
                  <span className="animate-spin mr-2">⏳</span>
                ) : (
                  <FaCheckCircle className="mr-2" />
                )}
                View Your Results
              </button>
            </div>
          </div>
        )}
        {/* Navigation Buttons */}
        <div className="flex justify-between mt-8">
          <button
            type="button"
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
            className="px-4 py-2 rounded bg-gray-200 text-gray-700 font-semibold flex items-center disabled:opacity-50"
          >
            <FaArrowLeft className="mr-2" />
            Back
          </button>
          {step < steps.length - 1 ? (
            <button
              type="button"
              onClick={() => setStep((s) => Math.min(steps.length - 1, s + 1))}
              className="px-4 py-2 rounded bg-blue-600 text-white font-semibold flex items-center hover:bg-blue-700 transition-all"
            >
              <span>Next</span>
              <FaArrowRight className="ml-2" />
            </button>
          ) : null}
        </div>
        {result && (
          <div className="mt-8 space-y-6 animate-fade-in">
            {/* Score Display */}
            {result.score && (
              <div className="bg-gradient-to-r from-green-100 to-blue-100 p-6 rounded-xl border border-green-200">
                <div className="text-center mb-4">
                  <div className="text-4xl font-bold text-green-600">
                    {result.score.total}/100
                  </div>
                  <div className="text-lg font-semibold text-gray-700">
                    {result.score.level}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="bg-white p-3 rounded-lg">
                    <div className="font-semibold text-gray-600">
                      Food Choices
                    </div>
                    <div className="text-lg font-bold text-green-600">
                      {result.score.breakdown.food_choices}
                    </div>
                  </div>
                  <div className="bg-white p-3 rounded-lg">
                    <div className="font-semibold text-gray-600">
                      Transportation
                    </div>
                    <div className="text-lg font-bold text-blue-600">
                      {result.score.breakdown.transportation}
                    </div>
                  </div>
                  <div className="bg-white p-3 rounded-lg">
                    <div className="font-semibold text-gray-600">
                      Daily Actions
                    </div>
                    <div className="text-lg font-bold text-purple-600">
                      {result.score.breakdown.daily_actions}
                    </div>
                  </div>
                  <div className="bg-white p-3 rounded-lg">
                    <div className="font-semibold text-gray-600">Clothing</div>
                    <div className="text-lg font-bold text-yellow-600">
                      {result.score.breakdown.clothing}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Analysis */}
            {result.analysis && (
              <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <h3 className="font-bold text-gray-800 mb-4 flex items-center">
                  <FaLeaf className="text-green-600 mr-2" />
                  Your Impact Today
                </h3>

                {result.analysis.impact_summary && (
                  <div className="bg-green-50 p-4 rounded-lg mb-4">
                    <p className="text-green-800 font-medium">
                      {result.analysis.impact_summary}
                    </p>
                  </div>
                )}

                {result.analysis.recommendations &&
                  result.analysis.recommendations.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-700 mb-2">
                        Recommendations:
                      </h4>
                      <ul className="space-y-2">
                        {result.analysis.recommendations.map(
                          (rec: string, index: number) => (
                            <li key={index} className="flex items-start">
                              <FaCheckCircle className="text-green-500 mt-1 mr-2 flex-shrink-0" />
                              <span className="text-gray-700">{rec}</span>
                            </li>
                          )
                        )}
                      </ul>
                    </div>
                  )}
              </div>
            )}

            {/* Item Classification */}
            {result.items && result.items.length > 0 && (
              <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <h3 className="font-bold text-gray-800 mb-4">Item Analysis</h3>
                {result.items.map((item: any, index: number) => (
                  <div key={index} className="bg-gray-50 p-4 rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <span className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm font-medium">
                          {item.type}
                        </span>
                        <span className="ml-2 text-gray-600 font-medium">
                          {item.category}
                        </span>
                      </div>
                      <span className="text-sm text-gray-500">
                        {Math.round(item.confidence * 100)}% confidence
                      </span>
                    </div>
                    {item.materials && item.materials.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {item.materials.map((material: string, idx: number) => (
                          <span
                            key={idx}
                            className="inline-block bg-green-100 text-green-700 px-2 py-1 rounded-full text-xs"
                          >
                            {material}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Start Over Button */}
            <div className="text-center">
              <button
                onClick={() => {
                  setResult(null);
                  setStep(0);
                  reset();
                }}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-all duration-200 flex items-center mx-auto"
              >
                <FaArrowLeft className="mr-2" />
                Take Another Assessment
              </button>
            </div>
          </div>
        )}
      </form>

      {/* Barcode Scanner Modal */}
      {showBarcodeScanner && (
        <BarcodeScanner
          onBarcodeDetected={handleBarcodeDetected}
          onClose={() => setShowBarcodeScanner(false)}
          productType="food"
        />
      )}

      {/* Food Category Confirmation Modal */}
      {showFoodCategoryConfirmation && pendingFoodProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full m-4">
            <div className="text-center">
              <h3 className="text-xl font-bold mb-4 text-gray-800">
                ⚠️ Category Confirmation
              </h3>
              <div className="mb-4">
                <p className="text-gray-600 mb-2">
                  We found a product, but we're not sure if it's a food item:
                </p>
                <div className="bg-gray-50 p-3 rounded-lg text-left">
                  <p><strong>Product:</strong> {pendingFoodProduct.name}</p>
                  <p><strong>Brand:</strong> {pendingFoodProduct.brand}</p>
                  <p><strong>AI detected category:</strong> {pendingFoodProduct.detected_category}</p>
                  <p><strong>Confidence:</strong> {Math.round(pendingFoodProduct.category_confidence * 100)}%</p>
                </div>
                <p className="text-gray-600 mt-3">
                  Is this actually a <strong>food or beverage</strong> product?
                </p>
              </div>
              <div className="flex gap-3 justify-center">
                <button
                  onClick={() => handleFoodCategoryConfirm(true)}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  ✅ Yes, it's food
                </button>
                <button
                  onClick={() => handleFoodCategoryConfirm(false)}
                  className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  ❌ No, wrong category
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Clothing Category Confirmation Modal */}
      {showClothingCategoryConfirmation && pendingClothingProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full m-4">
            <div className="text-center">
              <h3 className="text-xl font-bold mb-4 text-gray-800">
                ⚠️ Category Confirmation
              </h3>
              <div className="mb-4">
                <p className="text-gray-600 mb-2">
                  We found a product, but we're not sure if it's a clothing item:
                </p>
                <div className="bg-gray-50 p-3 rounded-lg text-left">
                  <p><strong>Product:</strong> {pendingClothingProduct.name}</p>
                  <p><strong>Brand:</strong> {pendingClothingProduct.brand}</p>
                  <p><strong>AI detected category:</strong> {pendingClothingProduct.detected_category}</p>
                  <p><strong>Confidence:</strong> {Math.round(pendingClothingProduct.category_confidence * 100)}%</p>
                </div>
                <p className="text-gray-600 mt-3">
                  Is this actually a <strong>clothing or textile</strong> product?
                </p>
              </div>
              <div className="flex gap-3 justify-center">
                <button
                  onClick={() => handleClothingCategoryConfirm(true)}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  ✅ Yes, it's clothing
                </button>
                <button
                  onClick={() => handleClothingCategoryConfirm(false)}
                  className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  ❌ No, wrong category
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
