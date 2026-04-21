"use client";

import Image from "next/image";
import { ArrowUp, ImagePlus, LoaderCircle, X } from "lucide-react";
import type { RefObject } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import type { ImageModel } from "@/lib/api";
import type { ImageConversationMode } from "@/store/image-conversations";
import { cn } from "@/lib/utils";

type ImageComposerProps = {
  mode: ImageConversationMode;
  prompt: string;
  model: ImageModel;
  imageCount: string;
  availableQuota: string;
  hasAnyGenerating: boolean;
  generatingCount: number;
  referenceImageName: string | null;
  referenceImagePreview: string | null;
  textareaRef: RefObject<HTMLTextAreaElement | null>;
  fileInputRef: RefObject<HTMLInputElement | null>;
  imageModelOptions: Array<{ label: string; value: ImageModel }>;
  onModeChange: (value: ImageConversationMode) => void;
  onPromptChange: (value: string) => void;
  onModelChange: (value: ImageModel) => void;
  onImageCountChange: (value: string) => void;
  onSubmit: () => void | Promise<void>;
  onPickReferenceImage: () => void;
  onReferenceImageChange: (file: File | null) => void | Promise<void>;
  onClearReferenceImage: () => void;
};

export function ImageComposer({
  mode,
  prompt,
  model,
  imageCount,
  availableQuota,
  hasAnyGenerating,
  generatingCount,
  referenceImageName,
  referenceImagePreview,
  textareaRef,
  fileInputRef,
  imageModelOptions,
  onModeChange,
  onPromptChange,
  onModelChange,
  onImageCountChange,
  onSubmit,
  onPickReferenceImage,
  onReferenceImageChange,
  onClearReferenceImage,
}: ImageComposerProps) {
  return (
    <div className="shrink-0 flex justify-center">
      <div style={{ width: "min(980px, 100%)" }}>
        {mode === "edit" && (
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(event) => {
              void onReferenceImageChange(event.target.files?.[0] ?? null);
            }}
          />
        )}

        {mode === "edit" && referenceImagePreview ? (
          <div className="mb-3 flex items-center gap-3 rounded-[28px] border border-stone-200/80 bg-white px-4 py-4 shadow-[0_18px_48px_rgba(28,25,23,0.08)]">
            <Image
              src={referenceImagePreview}
              alt={referenceImageName || "参考图预览"}
              width={56}
              height={56}
              unoptimized
              className="size-14 rounded-xl object-cover"
            />
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-medium text-stone-800">{referenceImageName}</div>
              <div className="text-xs text-stone-500">将基于这张图片进行编辑</div>
            </div>
            <button
              type="button"
              onClick={onClearReferenceImage}
              className="inline-flex size-8 items-center justify-center rounded-full text-stone-400 transition hover:bg-stone-100 hover:text-stone-700"
              aria-label="移除参考图"
            >
              <X className="size-4" />
            </button>
          </div>
        ) : null}

        <div className="overflow-hidden rounded-[32px] border border-stone-200/80 bg-white shadow-[0_18px_48px_rgba(28,25,23,0.08)]">
          <div
            className="relative cursor-text"
            onClick={() => {
              textareaRef.current?.focus();
            }}
          >
            <Textarea
              ref={textareaRef}
              value={prompt}
              onChange={(event) => onPromptChange(event.target.value)}
              placeholder={mode === "edit" ? "描述你希望如何修改这张参考图" : "输入你想要生成的画面"}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  void onSubmit();
                }
              }}
              className="min-h-[148px] resize-none rounded-[32px] border-0 bg-transparent px-6 pt-6 pb-20 text-[15px] leading-7 text-stone-900 shadow-none placeholder:text-stone-400 focus-visible:ring-0"
            />

            <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-white via-white/95 to-transparent px-4 pb-4 pt-6 sm:px-6">
              {mode === "edit" && (
                <div className="mb-3 flex flex-wrap items-center gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    className="h-10 rounded-full border-stone-200 bg-white px-4 text-sm font-medium text-stone-700 shadow-none"
                    onClick={onPickReferenceImage}
                  >
                    <ImagePlus className="size-4" />
                    {referenceImageName ? "重新上传参考图" : "上传参考图"}
                  </Button>
                </div>
              )}

              <div className="flex items-center justify-between gap-3">
                <div className="flex flex-wrap items-center gap-3">
                  <div className="rounded-full bg-stone-100 px-3 py-2 text-xs font-medium text-stone-600">剩余额度 {availableQuota}</div>
                  {hasAnyGenerating && (
                    <div className="flex items-center gap-1.5 rounded-full bg-amber-50 px-3 py-2 text-xs font-medium text-amber-700">
                      <LoaderCircle className="size-3 animate-spin" />
                      {generatingCount} 个任务进行中
                    </div>
                  )}
                  <Select value={model} onValueChange={(value) => onModelChange(value as ImageModel)}>
                    <SelectTrigger className="h-10 w-[164px] rounded-full border-stone-200 bg-white text-sm font-medium text-stone-700 shadow-none focus-visible:ring-0">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {imageModelOptions.map((item) => (
                        <SelectItem key={item.value} value={item.value}>
                          {item.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <div className="flex items-center gap-2 rounded-full border border-stone-200 bg-white px-3 py-1">
                    <span className="text-sm font-medium text-stone-700">张数</span>
                    <Input
                      type="number"
                      min="1"
                      max="10"
                      step="1"
                      value={imageCount}
                      onChange={(event) => onImageCountChange(event.target.value)}
                      className="h-8 w-[64px] border-0 bg-transparent px-0 text-center text-sm font-medium text-stone-700 shadow-none focus-visible:ring-0"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <ModeButton active={mode === "generate"} onClick={() => onModeChange("generate")}>
                      文生图
                    </ModeButton>
                    <ModeButton active={mode === "edit"} onClick={() => onModeChange("edit")}>
                      编辑图
                    </ModeButton>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => void onSubmit()}
                  disabled={!prompt.trim() || (mode === "edit" && !referenceImagePreview)}
                  className="inline-flex size-11 shrink-0 items-center justify-center rounded-full bg-stone-950 text-white transition hover:bg-stone-800 disabled:cursor-not-allowed disabled:bg-stone-300"
                  aria-label={mode === "edit" ? "编辑图片" : "生成图片"}
                >
                  <ArrowUp className="size-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ModeButton({
  active,
  children,
  onClick,
}: {
  active: boolean;
  children: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-full px-4 py-2 text-sm font-medium transition",
        active ? "bg-stone-950 text-white" : "bg-stone-100 text-stone-600 hover:bg-stone-200",
      )}
    >
      {children}
    </button>
  );
}
