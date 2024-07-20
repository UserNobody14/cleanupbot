"use client";

import React, { useState, ChangeEvent, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckIcon, UploadIcon } from "lucide-react";

type UploadStatus = "idle" | "uploading" | "success" | "error";

export function Upload(): JSX.Element {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>("idle");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setSelectedFiles(files);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      alert("Please select at least one file to upload.");
      return;
    }

    setUploadStatus("uploading");

    const formData = new FormData();
    selectedFiles.forEach((file, index) => {
      formData.append(`file${index}`, file);
    });

    try {
      const response = await fetch("http://localhost:8000/save_image", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        console.log("Upload successful");
        console.log(response);
      }
    } catch (error) {
      console.error("Upload failed:", error);
      setUploadStatus("error");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background">
      <div className="container max-w-3xl px-4 py-12 md:px-6 lg:py-16">
        <h1 className="text-3xl font-bold tracking-tighter text-center sm:text-4xl md:text-5xl">
          Clean Up Bot
        </h1>
        <div className="mt-8 space-y-4">
          <Card className="border-2 border-dashed border-primary/50 bg-primary/10 p-8 text-center transition-colors hover:border-primary">
            <CardContent>
              <div className="flex flex-col items-center justify-center space-y-4">
                <UploadIcon className="h-12 w-12 text-primary" />
                <p className="text-lg font-medium text-primary">
                  Drag and drop your images here
                </p>
                <p className="text-muted-foreground">or click to upload</p>
                <input
                  type="file"
                  multiple
                  className="hidden"
                  onChange={handleFileChange}
                  accept="image/*"
                  ref={fileInputRef}
                />
                <Button onClick={handleUploadClick}>Upload Images</Button>
              </div>
            </CardContent>
          </Card>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
            {selectedFiles.map((file, index) => (
              <img
                key={index}
                src={URL.createObjectURL(file)}
                width={500}
                height={500}
                alt={`Uploaded Image ${index + 1}`}
                className="aspect-square w-full rounded-md object-cover"
              />
            ))}
          </div>
          <div className="mt-6">
            <Button
              className="inline-flex items-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow-sm transition-colors hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
              onClick={handleUpload}
              disabled={
                uploadStatus === "uploading" || selectedFiles.length === 0
              }
            >
              {uploadStatus === "uploading" ? "Uploading..." : "Analyze Image"}
            </Button>
          </div>
          {uploadStatus !== "idle" && (
            <div className="mt-6 flex items-center justify-center">
              <div className="flex items-center gap-2">
                {uploadStatus === "success" ? (
                  <>
                    <CheckIcon className="h-6 w-6 text-green-500" />
                    <p className="text-sm font-medium text-foreground">
                      Image is clean
                    </p>
                  </>
                ) : uploadStatus === "error" ? (
                  <p className="text-sm font-medium text-red-500">
                    Upload failed. Please try again.
                  </p>
                ) : null}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
