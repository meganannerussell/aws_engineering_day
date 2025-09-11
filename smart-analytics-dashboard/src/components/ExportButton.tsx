import React from "react";
import { motion } from "framer-motion";
import { Download } from "lucide-react";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";

const ExportButton: React.FC = () => {
  const handleExportPDF = async () => {
    try {
      // Get the main content area
      const element = document.querySelector(".results-container");
      if (!element) {
        console.error("Could not find results container");
        return;
      }

      // Create canvas from the element
      const canvas = await html2canvas(element as HTMLElement, {
        useCORS: true,
        allowTaint: true,
        background: "#ffffff",
        width: element.scrollWidth,
        height: element.scrollHeight,
      });

      // Create PDF
      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("p", "mm", "a4");

      // Calculate dimensions to fit the content
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
      const imgX = (pdfWidth - imgWidth * ratio) / 2;
      const imgY = 0;

      pdf.addImage(
        imgData,
        "PNG",
        imgX,
        imgY,
        imgWidth * ratio,
        imgHeight * ratio
      );

      // Save the PDF
      pdf.save("analytics-report.pdf");
    } catch (error) {
      console.error("Error generating PDF:", error);
      alert("Failed to export PDF. Please try again.");
    }
  };

  return (
    <motion.button
      className="export-button"
      onClick={handleExportPDF}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        className="export-button__icon"
        whileHover={{ rotate: 5 }}
        transition={{ duration: 0.2 }}
      >
        <Download size={20} />
      </motion.div>
      <span className="export-button__text">Export PDF</span>
    </motion.button>
  );
};

export default ExportButton;
