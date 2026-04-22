"use client";

import { Link2, LoaderCircle, Save } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

import { useSettingsStore } from "../store";

export function ProxySettingsCard() {
  const config = useSettingsStore((state) => state.config);
  const isLoadingConfig = useSettingsStore((state) => state.isLoadingConfig);
  const isSavingConfig = useSettingsStore((state) => state.isSavingConfig);
  const setProxy = useSettingsStore((state) => state.setProxy);
  const saveConfig = useSettingsStore((state) => state.saveConfig);

  const proxy = config?.proxy ?? "";

  return (
    <Card className="rounded-2xl border-white/80 bg-white/90 shadow-sm">
      <CardContent className="space-y-6 p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-xl bg-stone-100">
              <Link2 className="size-5 text-stone-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold tracking-tight">全局代理</h2>
              <p className="text-sm text-stone-500">为系统中的出站请求配置统一代理，保存后会立即生效。</p>
            </div>
          </div>
          <Badge variant={proxy.trim() ? "success" : "secondary"} className="w-fit rounded-md px-2.5 py-1">
            {proxy.trim() ? "已配置" : "未配置"}
          </Badge>
        </div>

        {isLoadingConfig ? (
          <div className="flex items-center justify-center py-10">
            <LoaderCircle className="size-5 animate-spin text-stone-400" />
          </div>
        ) : (
          <>
            <div className="space-y-2">
              <label className="text-sm font-medium text-stone-700">代理地址</label>
              <Input
                value={proxy}
                onChange={(event) => setProxy(event.target.value)}
                placeholder="http://user:pass@127.0.0.1:7890"
                className="h-11 rounded-xl border-stone-200 bg-white"
              />
              <p className="text-sm text-stone-500">
                留空表示不使用代理。请按完整地址填写，例如 `http://127.0.0.1:7890`、`http://用户名:密码@127.0.0.1:7890` 或 `socks5://127.0.0.1:7890`。
              </p>
            </div>

            <div className="flex justify-end">
              <Button
                className="h-10 rounded-xl bg-stone-950 px-5 text-white hover:bg-stone-800"
                onClick={() => void saveConfig()}
                disabled={isSavingConfig}
              >
                {isSavingConfig ? <LoaderCircle className="size-4 animate-spin" /> : <Save className="size-4" />}
                保存配置
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
