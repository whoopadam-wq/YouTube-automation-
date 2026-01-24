"use client";

import { cn } from "@/lib/utils";
import { UploadCloudIcon } from "lucide-react";
import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { TooltipProvider } from "./tooltip";

type DropzoneComponentProps = {
  onDrop: (acceptedFiles: File[]) => void;
  className?: string;
  children?: React.ReactNode;
};

const Dropzone = ({ onDrop, className, children }: DropzoneComponentProps) => {
  const onDropCallback = useCallback(
    (acceptedFiles: File[]) => {
      onDrop(acceptedFiles);
    },
    [onDrop]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: onDropCallback,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "flex flex-col items-center justify-center w-full h-32 px-4 py-6 text-center border-2 border-dashed rounded-lg cursor-pointer border-stone-300 dark:border-stone-700 bg-stone-50 dark:bg-stone-900 hover:bg-stone-100 dark:hover:bg-stone-800",
        { "border-primary dark:border-primary": isDragActive },
        className
      )}
    >
      <TooltipProvider>
        <input {...getInputProps()} />
        {children ? (
          children
        ) : isDragActive ? (
          <p className="text-stone-600 dark:text-stone-300">
            Drop the files here ...
          </p>
        ) : (
          <div className="flex flex-col items-center justify-center gap-2 text-stone-600 dark:text-stone-300">
            <UploadCloudIcon className="w-8 h-8" />
            <p className="text-sm">
              Drag & drop files here, or click to select files
            </p>
          </div>
        )}
      </TooltipProvider>
    </div>
  );
};

export default Dropzone;
