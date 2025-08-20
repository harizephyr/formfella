"use client";

import { useState, useCallback, useEffect } from "react";
import { motion } from "framer-motion";
import { useDropzone } from "react-dropzone";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  Upload, 
  FileText, 
  X, 
  CheckCircle, 
  AlertCircle,
  ArrowRight,
  FileCheck,
  Zap
} from "lucide-react";
import Link from "next/link";
import { Navigation } from "@/components/navigation";
import { toast } from "sonner";
import PurpleWhiteForm from "@/components/purple-white-form";
import { useParams } from "next/navigation";
import cookies from "js-cookie";


const fadeInUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
};

const staggerChildren = {
  visible: {
    transition: {
      staggerChildren: 0.1
    }
  }
};







export default function UploadPage() {
  const params = useParams();
  
  useEffect(() => {
    if (params?.code) {
      cookies.set("access_token", params.code);
      console.log("Access token set:", params.code);
    }
  }, [params]);

  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [questions, setQuestions] = useState([]);

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      progress: 0,
      status: 'uploading',
      id: Math.random().toString(36).substring(7)
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);

    // Simulate upload progress
    newFiles.forEach((uploadFile, index) => {
      let progress = 0;
      const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 100) {
          progress = 100;
          clearInterval(interval);
          setUploadedFiles(prev => 
            prev.map(f => 
              f.id === uploadFile.id 
                ? { ...f, progress: 100, status: 'completed' }
                : f
            )
          );
          toast.success(`${uploadFile.file.name} uploaded successfully!`);
        } else {
          setUploadedFiles(prev => 
            prev.map(f => 
              f.id === uploadFile.id 
                ? { ...f, progress }
                : f
            )
          );
        }
      }, 200);
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: true
  });

  const removeFile = (id) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== id));
  };

  const process_pdf_and_get_questions = async () => {
    if (uploadedFiles.length === 0) {
      toast.error("Please upload at least one file");
      return;
    }
  
    setIsProcessing(true);
    const loadingToast = toast.loading("Analyzing PDF with AI...");
  
    try {
      const formData = new FormData();
      uploadedFiles.forEach((fileData) => {
        formData.append("files", fileData.file);
      });
  
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/process`, {
        headers: {
          'Authorization': `Bearer ${document.cookie
            .split('; ')
            .find(row => row.startsWith('access_token='))
            ?.split('=')[1]}`
        },
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to process PDF");
      }
  
      const data = await response.json();
      console.log("PDF processing successful:", data);
      setQuestions(data); // assuming data is an array of Question objects
  
      toast.success("PDF processed successfully!");
    } catch (error) {
      console.error("Error processing PDF:", error);
      toast.error(error instanceof Error ? error.message : "Failed to process PDF");
    } finally {
      setIsProcessing(false);
      toast.dismiss(loadingToast);
    }
  };


  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <>
    {questions.length > 0 ? (
      <PurpleWhiteForm formData={{form_id: questions[0].form_id, questions: questions[0].questions, total_questions: questions[0].questions.length}} />
    ) : (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-background/80">
      <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] dark:bg-grid-slate-700/25" />
      
      <Navigation />

      <div className="relative pt-20 px-4 pb-16">
        <div className="container mx-auto max-w-4xl">
          <motion.div 
            className="space-y-8"
            initial="hidden"
            animate="visible"
            variants={staggerChildren}
          >
            {/* Header */}
            <motion.div variants={fadeInUp} className="text-center space-y-4">
              <h1 className="text-3xl md:text-4xl font-bold">Upload Your PDF Forms</h1>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Drag and drop your PDF forms or click to browse. Our AI will analyze and extract form fields automatically.
              </p>
            </motion.div>

            {/* Upload Zone */}
            <motion.div variants={fadeInUp}>
              <Card className="p-8 bg-background/50 backdrop-blur-sm border-2 border-dashed border-border hover:border-primary/50 transition-colors">
                <div
                  {...getRootProps()}
                  className={`cursor-pointer text-center space-y-6 ${
                    isDragActive ? 'scale-105' : ''
                  } transition-transform duration-200`}
                >
                  <input {...getInputProps()} />
                  
                  <div className="w-20 h-20 mx-auto bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                    <Upload className="w-10 h-10 text-white" />
                  </div>
                  
                  <div className="space-y-2">
                    <h3 className="text-xl font-semibold">
                      {isDragActive ? "Drop files here" : "Drag & drop PDF files"}
                    </h3>
                    <p className="text-muted-foreground">
                      or <span className="text-primary font-medium">click to browse</span>
                    </p>
                  </div>

                  <div className="flex items-center justify-center gap-8 text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <FileCheck className="w-4 h-4" />
                      PDF files only
                    </div>
                    <div className="flex items-center gap-2">
                      <Zap className="w-4 h-4" />
                      Max 50MB per file
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>

            {/* Upload Progress */}
            {uploadedFiles.length > 0 && (
              <motion.div 
                variants={fadeInUp}
                initial="hidden"
                animate="visible"
              >
                <Card className="p-6 bg-background/50 backdrop-blur-sm border-0 shadow-lg">
                  <h3 className="font-semibold mb-4 flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Uploaded Files ({uploadedFiles.length})
                  </h3>
                  
                  <div className="space-y-4">
                    {uploadedFiles.map((uploadFile) => (
                      <div key={uploadFile.id} className="flex items-center gap-4 p-4 border rounded-lg">
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center flex-shrink-0">
                          <FileText className="w-5 h-5 text-white" />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-2">
                            <p className="font-medium truncate">{uploadFile.file.name}</p>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="flex items-center gap-1">
                                {uploadFile.status === 'completed' && (
                                  <>
                                    <CheckCircle className="w-3 h-3 text-green-500" />
                                    Completed
                                  </>
                                )}
                                {uploadFile.status === 'uploading' && (
                                  <>
                                    <div className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                                    Uploading
                                  </>
                                )}
                                {uploadFile.status === 'error' && (
                                  <>
                                    <AlertCircle className="w-3 h-3 text-red-500" />
                                    Error
                                  </>
                                )}
                              </Badge>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => removeFile(uploadFile.id)}
                                className="w-8 h-8"
                              >
                                <X className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                          
                          <div className="space-y-2">
                            <Progress value={uploadFile.progress} className="h-2" />
                            <div className="flex items-center justify-between text-sm text-muted-foreground">
                              <span>{formatFileSize(uploadFile.file.size)}</span>
                              <span>{uploadFile.progress.toFixed(0)}%</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </motion.div>
            )}

            {/* Action Buttons */}
            {uploadedFiles.some(f => f.status === 'completed') && (
              <motion.div 
                variants={fadeInUp}
                initial="hidden"
                animate="visible"
                className="flex flex-col sm:flex-row gap-4 justify-center"
              >
                <Button
                  size="lg"
                  onClick={process_pdf_and_get_questions}
                  disabled={isProcessing}
                  className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-lg px-8 py-6"
                >
                  {isProcessing ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      Processing with AI...
                    </>
                  ) : (
                    <>
                      Start AI Analysis
                      <ArrowRight className="ml-2 w-5 h-5" />
                    </>
                  )}
                </Button>
                
                <Button variant="outline" size="lg" className="text-lg px-8 py-6" asChild>
                  <Link href="/dashboard">
                    Back to Dashboard
                  </Link>
                </Button>
              </motion.div>
            )}

            {/* Help Section */}
            <motion.div variants={fadeInUp}>
              <Card className="p-6 bg-muted/30 border-0">
                <h3 className="font-semibold mb-4">Upload Tips</h3>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div className="space-y-2">
                    <h4 className="font-medium">Supported formats:</h4>
                    <ul className="text-muted-foreground space-y-1">
                      <li>• PDF files (.pdf)</li>
                      <li>• Maximum size: 50MB per file</li>
                      <li>• Text-based PDFs work best</li>
                    </ul>
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-medium">For best results:</h4>
                    <ul className="text-muted-foreground space-y-1">
                      <li>• Ensure text is clear and readable</li>
                      <li>• Avoid heavily compressed files</li>
                      <li>• Remove password protection</li>
                    </ul>
                  </div>
                </div>
              </Card>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>)}
    </>
  );
}