import React, { useState, useRef } from "react";
import { motion } from "framer-motion";
import { Play, Loader2, ChevronLeft, Upload, FileText, X } from "lucide-react";

interface DatasetAnalyzerProps {
  onAnalysisComplete: (data: any) => void;
  onLoadingChange: (loading: boolean) => void;
  onDrawerToggle?: (collapsed: boolean) => void;
}

const DatasetAnalyzer: React.FC<DatasetAnalyzerProps> = ({
  onAnalysisComplete,
  onLoadingChange,
  onDrawerToggle,
}) => {
  const [selectedDataset, setSelectedDataset] =
    useState<string>("data_set_1.csv");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [uploadedDatasets, setUploadedDatasets] = useState<
    Array<{ value: string; label: string; file: File }>
  >([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const sampleDatasets = [
    { value: "data_set_1.csv", label: "Beauty Products Survey" },
    { value: "data_set_2.csv", label: "Customer Service Experience" },
    { value: "data_set_3.csv", label: "Mobile App User Experience" },
    { value: "data_set_4.csv", label: "E-commerce Feedback" },
    { value: "data_set_5.csv", label: "Restaurant Reviews" },
    { value: "data_set_6.csv", label: "Software Product Feedback" },
    { value: "blind_data.csv", label: "Blind Data Analysis" },
  ];

  const datasets = [...sampleDatasets, ...uploadedDatasets];

  const handleDatasetChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedDataset(event.target.value);
  };

  const toggleCollapsed = () => {
    const newCollapsedState = !isCollapsed;
    setIsCollapsed(newCollapsedState);
    onDrawerToggle?.(newCollapsedState);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.name.toLowerCase().endsWith(".csv")) {
      alert("Please upload a CSV file");
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert("File size must be less than 10MB");
      return;
    }

    setIsUploading(true);

    // Create a unique identifier for the uploaded file
    const fileId = `uploaded_${Date.now()}_${file.name}`;
    const fileName = file.name.replace(".csv", "");

    // Add to uploaded datasets
    const newUploadedDataset = {
      value: fileId,
      label: `📁 ${fileName}`,
      file: file,
    };

    setUploadedDatasets((prev) => [...prev, newUploadedDataset]);
    setSelectedDataset(fileId);
    setIsUploading(false);

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const removeUploadedDataset = (fileId: string) => {
    setUploadedDatasets((prev) =>
      prev.filter((dataset) => dataset.value !== fileId)
    );
    if (selectedDataset === fileId) {
      setSelectedDataset("data_set_1.csv");
    }
  };

  const getCachedData = (dataset: string) => {
    try {
      const cached = localStorage.getItem(`analytics_cache_${dataset}`);
      if (cached) {
        const data = JSON.parse(cached);
        // Check if cache is less than 24 hours old
        const cacheTime = data.cacheTime || 0;
        const now = Date.now();
        const twentyFourHours = 24 * 60 * 60 * 1000;

        if (now - cacheTime < twentyFourHours) {
          console.log(`📦 Using cached data for ${dataset}`);
          return data.analyticsData;
        } else {
          console.log(`🗑️ Cache expired for ${dataset}`);
          localStorage.removeItem(`analytics_cache_${dataset}`);
        }
      }
    } catch (error) {
      console.warn("Failed to load cached data:", error);
    }
    return null;
  };

  const setCachedData = (dataset: string, data: any) => {
    try {
      const cacheData = {
        analyticsData: data,
        cacheTime: Date.now(),
      };
      localStorage.setItem(
        `analytics_cache_${dataset}`,
        JSON.stringify(cacheData)
      );
      console.log(`💾 Cached data for ${dataset}`);
    } catch (error) {
      console.warn("Failed to cache data:", error);
    }
  };

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    onLoadingChange(true);

    try {
      // Check for cached data first
      const cachedData = getCachedData(selectedDataset);
      if (cachedData) {
        onAnalysisComplete(cachedData);
        setIsAnalyzing(false);
        onLoadingChange(false);
        return;
      }

      // Check if this is an uploaded file
      const uploadedDataset = uploadedDatasets.find(
        (ds) => ds.value === selectedDataset
      );

      if (uploadedDataset) {
        // Handle uploaded file - send as FormData
        const formData = new FormData();
        formData.append("file", uploadedDataset.file);
        formData.append("dataset", selectedDataset);

        const response = await fetch(
          "http://localhost:5002/api/analyze-upload",
          {
            method: "POST",
            body: formData,
          }
        );

        if (!response.ok) {
          throw new Error(`Analysis failed: ${response.statusText}`);
        }

        const analysisData = await response.json();
        setCachedData(selectedDataset, analysisData);
        onAnalysisComplete(analysisData);
      } else {
        // Handle sample dataset - send as JSON
        const response = await fetch("http://localhost:5002/api/analyze", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            dataset: selectedDataset,
          }),
        });

        if (!response.ok) {
          throw new Error(`Analysis failed: ${response.statusText}`);
        }

        const analysisData = await response.json();
        setCachedData(selectedDataset, analysisData);
        onAnalysisComplete(analysisData);
      }
    } catch (error) {
      console.error("Analysis error:", error);
      // Fallback to mock data if backend is not available
      console.log("Falling back to mock data...");
      setTimeout(() => {
        const mockData = generateMockAnalysisData(selectedDataset);
        setCachedData(selectedDataset, mockData);
        onAnalysisComplete(mockData);
        setIsAnalyzing(false);
        onLoadingChange(false);
      }, 1500);
      return;
    } finally {
      setIsAnalyzing(false);
      onLoadingChange(false);
    }
  };

  // Mock data generator for demo purposes
  const generateMockAnalysisData = (dataset: string) => {
    const baseData = {
      project_metadata: {
        project_title: `Analysis of ${dataset
          .replace(".csv", "")
          .replace("_", " ")
          .toUpperCase()}`,
        question_text: "What are your thoughts and experiences?",
        total_responses: Math.floor(Math.random() * 200) + 100,
        processing_time_seconds: Math.random() * 30 + 10,
        timestamp: new Date().toISOString(),
        pipeline_version: "clean_structured_v1",
        services_used: {
          bedrock_embeddings: true,
          bedrock_llm: true,
          comprehend_sentiment: true,
          dbscan_clustering: true,
          intelligent_caching: true,
        },
      },
      summary_stats: {
        total_topics: Math.floor(Math.random() * 8) + 5,
        avg_responses_per_topic: Math.floor(Math.random() * 20) + 10,
        overall_sentiment_score: Math.random() * 0.6 + 0.2,
        pii_detection_rate: Math.random() * 0.1,
        processing_rate: Math.random() * 50 + 20,
        cache_performance: {
          embedding_cache_size: Math.floor(Math.random() * 100),
          sentiment_cache_size: Math.floor(Math.random() * 50),
        },
      },
      topics: generateMockTopics(),
    };

    return baseData;
  };

  const generateMockTopics = () => {
    const topicTemplates = [
      { label: "Product Quality", sentiment: 0.7 },
      { label: "User Experience", sentiment: 0.6 },
      { label: "Customer Service", sentiment: 0.5 },
      { label: "Performance Issues", sentiment: 0.3 },
      { label: "Pricing Concerns", sentiment: 0.4 },
      { label: "Feature Requests", sentiment: 0.8 },
      { label: "Design Feedback", sentiment: 0.6 },
      { label: "Delivery Experience", sentiment: 0.5 },
    ];

    const numTopics = Math.floor(Math.random() * 6) + 4;
    const topics = [];

    for (let i = 0; i < numTopics; i++) {
      const template = topicTemplates[i % topicTemplates.length];
      const count = Math.floor(Math.random() * 50) + 10;

      topics.push({
        topic_id: `topic_${i}`,
        label: template.label,
        count: count,
        percentage: Math.round((count / 200) * 100 * 10) / 10,
        sentiment_mean: template.sentiment + (Math.random() - 0.5) * 0.3,
        sentiment_distribution: {
          positive: Math.floor(count * template.sentiment),
          negative: Math.floor(count * (1 - template.sentiment) * 0.6),
          neutral: Math.floor(count * (1 - template.sentiment) * 0.4),
          mixed: Math.floor(count * 0.1),
        },
        examples: [
          `Example response about ${template.label.toLowerCase()}`,
          `Another comment regarding ${template.label.toLowerCase()}`,
          `Feedback on ${template.label.toLowerCase()} experience`,
        ],
      });
    }

    return topics.sort((a, b) => b.count - a.count);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`dataset-analyzer ${isCollapsed ? "collapsed" : ""}`}
    >
      <div className="dataset-analyzer__collapsed-icon">🔬</div>
      <div className="dataset-analyzer__content">
        <h3 className="dataset-analyzer__title">
          <span className="dataset-analyzer__icon">🔬</span>
          Text Analytics Pipeline
        </h3>

        <div className="dataset-analyzer__form">
          {/* CSV Upload Section */}
          <div className="csv-uploader">
            <label className="csv-uploader__label">
              <Upload size={16} />
              Upload CSV Dataset
            </label>
            <div className="csv-uploader__container">
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFileUpload}
                className="csv-uploader__input"
                disabled={isAnalyzing || isUploading}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="csv-uploader__button"
                disabled={isAnalyzing || isUploading}
              >
                {isUploading ? (
                  <>
                    <Loader2 size={16} />
                    Uploading...
                  </>
                ) : (
                  <>
                    <FileText size={16} />
                    Choose File
                  </>
                )}
              </button>
            </div>
            <p className="csv-uploader__hint">
              Upload a CSV file (max 10MB) with text data to analyze
            </p>
          </div>

          {/* Dataset Selector */}
          <div className="dataset-selector">
            <label
              htmlFor="dataset-analyzer-select"
              className="dataset-selector__label"
            >
              Select Dataset to Analyze:
            </label>
            <select
              id="dataset-analyzer-select"
              value={selectedDataset}
              onChange={handleDatasetChange}
              className="dataset-selector__select"
              disabled={isAnalyzing}
            >
              {sampleDatasets.map((dataset) => (
                <option key={dataset.value} value={dataset.value}>
                  {dataset.label}
                </option>
              ))}
              {uploadedDatasets.length > 0 && (
                <optgroup label="Uploaded Files">
                  {uploadedDatasets.map((dataset) => (
                    <option key={dataset.value} value={dataset.value}>
                      {dataset.label}
                    </option>
                  ))}
                </optgroup>
              )}
            </select>
          </div>

          {/* Uploaded Files List */}
          {uploadedDatasets.length > 0 && (
            <div className="uploaded-files">
              <h4 className="uploaded-files__title">Uploaded Files:</h4>
              <div className="uploaded-files__list">
                {uploadedDatasets.map((dataset) => (
                  <div key={dataset.value} className="uploaded-file">
                    <FileText size={14} />
                    <span className="uploaded-file__name">
                      {dataset.label.replace("📁 ", "")}
                    </span>
                    <button
                      onClick={() => removeUploadedDataset(dataset.value)}
                      className="uploaded-file__remove"
                      disabled={isAnalyzing}
                    >
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <motion.button
            className="analyze-button"
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            whileHover={{ scale: isAnalyzing ? 1 : 1.05 }}
            whileTap={{ scale: isAnalyzing ? 1 : 0.95 }}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="analyze-button__icon" size={20} />
                <span className="analyze-button__text">Analyzing...</span>
              </>
            ) : (
              <>
                <Play className="analyze-button__icon" size={20} />
                <span className="analyze-button__text">Analyze Dataset</span>
              </>
            )}
          </motion.button>
        </div>

        <div className="dataset-analyzer__info">
          <p className="dataset-analyzer__description">
            This will process your selected dataset using our advanced text
            analytics pipeline:
          </p>
          <ul className="dataset-analyzer__features">
            <li>🧮 DBSCAN clustering for unstructured data</li>
            <li>🏷️ LLM-powered topic labeling</li>
            <li>😊 Advanced sentiment analysis</li>
            <li>🔒 PII detection and redaction</li>
            <li>⚡ Intelligent caching for performance</li>
          </ul>
        </div>
      </div>
      <button
        className={`dataset-analyzer__toggle-arrow ${
          isCollapsed ? "collapsed" : ""
        }`}
        onClick={toggleCollapsed}
        aria-label={isCollapsed ? "Expand drawer" : "Collapse drawer"}
      >
        <ChevronLeft className="arrow-icon" size={16} />
      </button>
    </motion.div>
  );
};

export default DatasetAnalyzer;
