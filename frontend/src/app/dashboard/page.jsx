"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Upload, 
  FileText, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Plus,
  Search,
  Filter,
  Download,
  Eye,
  Trash2,
  BarChart3,
  Users,
  Zap,
  Loader
} from "lucide-react";
import Link from "next/link";
import { Navigation } from "@/components/navigation";
import { Input } from "@/components/ui/input";

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

// Mock data for demonstration
const recentForms = [
  {
    id: 1,
    name: "Tax Form 1040.pdf",
    status: "completed",
    uploadDate: "2024-01-15",
    fields: 12,
    size: "2.4 MB"
  },
  {
    id: 2,
    name: "Loan Application.pdf",
    status: "processing",
    uploadDate: "2024-01-14",
    fields: 8,
    size: "1.8 MB"
  },
  {
    id: 3,
    name: "Insurance Claim.pdf",
    status: "pending",
    uploadDate: "2024-01-13",
    fields: 15,
    size: "3.2 MB"
  },
  {
    id: 4,
    name: "Employment Form.pdf",
    status: "completed",
    uploadDate: "2024-01-12",
    fields: 6,
    size: "1.1 MB"
  }
];

const templates = [
  {
    id: 1,
    name: "Tax Forms",
    description: "Common tax form templates",
    count: 12,
    icon: FileText
  },
  {
    id: 2,
    name: "Legal Documents",
    description: "Legal form templates",
    count: 8,
    icon: FileText
  },
  {
    id: 3,
    name: "Business Forms",
    description: "Business application forms",
    count: 15,
    icon: FileText
  }
];

export default function Dashboard() {
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
  //  redirect to upload page
  window.location.href = "/dashboard/upload";
  }, []);

  if (true) {
    return <div className="flex items-center justify-center h-screen"><Loader className="w-5 h-5 mr-2 animate-spin" />Loading...</div>;
  }

  const getStatusColor = (status) => {
    switch (status) {
      case "completed":
        return "bg-green-500";
      case "processing":
        return "bg-blue-500";
      case "pending":
        return "bg-yellow-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-4 h-4" />;
      case "processing":
        return <Clock className="w-4 h-4" />;
      case "pending":
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-background/80">
      <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))] dark:bg-grid-slate-700/25" />
      
      <Navigation />

      <div className="relative pt-20 px-4 pb-16">
        <div className="container mx-auto max-w-7xl">
          {/* Header */}
          <motion.div 
            className="mb-8"
            initial="hidden"
            animate="visible"
            variants={staggerChildren}
          >
            <motion.div variants={fadeInUp} className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
              <div>
                <h1 className="text-3xl md:text-4xl font-bold mb-2">Dashboard</h1>
                <p className="text-muted-foreground text-lg">Manage your PDF forms and track processing status</p>
              </div>
              <Button asChild size="lg" className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600">
                <Link href="/dashboard/upload">
                  <Plus className="w-5 h-5 mr-2" />
                  Upload New PDF
                </Link>
              </Button>
            </motion.div>

            {/* Stats Cards */}
            <motion.div variants={fadeInUp} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {[
                {
                  title: "Total Forms",
                  value: "24",
                  change: "+12%",
                  icon: FileText,
                  color: "from-blue-500 to-blue-600"
                },
                {
                  title: "Processed Today",
                  value: "8",
                  change: "+3",
                  icon: Zap,
                  color: "from-green-500 to-green-600"
                },
                {
                  title: "Processing Time",
                  value: "2.3s",
                  change: "-0.5s",
                  icon: Clock,
                  color: "from-purple-500 to-purple-600"
                },
                {
                  title: "Success Rate",
                  value: "99.2%",
                  change: "+0.8%",
                  icon: BarChart3,
                  color: "from-orange-500 to-orange-600"
                }
              ].map((stat, index) => (
                <Card key={index} className="p-6 bg-background/50 backdrop-blur-sm border-0 shadow-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                      <p className="text-2xl font-bold">{stat.value}</p>
                      <p className="text-sm text-green-600">{stat.change}</p>
                    </div>
                    <div className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-xl flex items-center justify-center`}>
                      <stat.icon className="w-6 h-6 text-white" />
                    </div>
                  </div>
                </Card>
              ))}
            </motion.div>
          </motion.div>

          {/* Main Content */}
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Recent Forms */}
            <motion.div 
              className="lg:col-span-2 space-y-6"
              initial="hidden"
              animate="visible"
              variants={staggerChildren}
            >
              <motion.div variants={fadeInUp}>
                <Card className="p-6 bg-background/50 backdrop-blur-sm border-0 shadow-lg">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold">Recent Forms</h2>
                    <div className="flex items-center gap-2">
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <Input
                          placeholder="Search forms..."
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          className="pl-10 w-64"
                        />
                      </div>
                      <Button variant="outline" size="icon">
                        <Filter className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="space-y-4">
                    {recentForms.map((form, index) => (
                      <motion.div
                        key={form.id}
                        variants={fadeInUp}
                        className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                      >
                        <div className="flex items-center gap-4">
                          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                            <FileText className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <h3 className="font-semibold">{form.name}</h3>
                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                              <span>{form.fields} fields</span>
                              <span>{form.size}</span>
                              <span>Uploaded {new Date(form.uploadDate).toLocaleDateString()}</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-3">
                          <Badge variant="outline" className="flex items-center gap-1">
                            <div className={`w-2 h-2 rounded-full ${getStatusColor(form.status)}`} />
                            {getStatusIcon(form.status)}
                            <span className="capitalize">{form.status}</span>
                          </Badge>
                          
                          <div className="flex items-center gap-1">
                            <Button variant="ghost" size="icon">
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button variant="ghost" size="icon">
                              <Download className="w-4 h-4" />
                            </Button>
                            <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive">
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>

                  <div className="mt-6 text-center">
                    <Button variant="outline">View All Forms</Button>
                  </div>
                </Card>
              </motion.div>
            </motion.div>

            {/* Sidebar */}
            <motion.div 
              className="space-y-6"
              initial="hidden"
              animate="visible"
              variants={staggerChildren}
            >
              {/* Quick Actions */}
              <motion.div variants={fadeInUp}>
                <Card className="p-6 bg-background/50 backdrop-blur-sm border-0 shadow-lg">
                  <h3 className="font-semibold mb-4">Quick Actions</h3>
                  <div className="space-y-3">
                    <Button asChild className="w-full justify-start" variant="outline">
                      <Link href="/upload">
                        <Upload className="w-4 h-4 mr-2" />
                        Upload PDF
                      </Link>
                    </Button>
                    <Button asChild className="w-full justify-start" variant="outline">
                      <Link href="/templates">
                        <FileText className="w-4 h-4 mr-2" />
                        Browse Templates
                      </Link>
                    </Button>
                    <Button asChild className="w-full justify-start" variant="outline">
                      <Link href="/analytics">
                        <BarChart3 className="w-4 h-4 mr-2" />
                        View Analytics
                      </Link>
                    </Button>
                  </div>
                </Card>
              </motion.div>

              {/* Template Library */}
              <motion.div variants={fadeInUp}>
                <Card className="p-6 bg-background/50 backdrop-blur-sm border-0 shadow-lg">
                  <h3 className="font-semibold mb-4">Template Library</h3>
                  <div className="space-y-3">
                    {templates.map((template) => (
                      <div key={template.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
                        <div className="flex items-center gap-3">
                          <template.icon className="w-5 h-5 text-muted-foreground" />
                          <div>
                            <p className="font-medium text-sm">{template.name}</p>
                            <p className="text-xs text-muted-foreground">{template.description}</p>
                          </div>
                        </div>
                        <Badge variant="secondary" className="text-xs">
                          {template.count}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </Card>
              </motion.div>

              {/* Processing Status */}
              <motion.div variants={fadeInUp}>
                <Card className="p-6 bg-background/50 backdrop-blur-sm border-0 shadow-lg">
                  <h3 className="font-semibold mb-4">Current Processing</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Loan Application.pdf</span>
                        <span className="text-sm text-muted-foreground">78%</span>
                      </div>
                      <Progress value={78} className="h-2" />
                      <p className="text-xs text-muted-foreground mt-1">Analyzing fields...</p>
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Insurance Form.pdf</span>
                        <span className="text-sm text-muted-foreground">42%</span>
                      </div>
                      <Progress value={42} className="h-2" />
                      <p className="text-xs text-muted-foreground mt-1">Extracting data...</p>
                    </div>
                  </div>
                </Card>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}